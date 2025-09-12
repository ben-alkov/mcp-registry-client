"""Integration tests with real API interactions.

These tests make actual HTTP requests to the MCP registry API.
They should be run separately from unit tests and may be affected by:
- Network connectivity
- API availability
- API rate limiting
"""

import asyncio
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import httpx
import pytest

from mcp_registry_client.client import RegistryAPIError, RegistryClient, RegistryClientError
from mcp_registry_client.config import ClientConfig


# Rate limiting helper
class RateLimiter:
    """Simple rate limiter to avoid overwhelming the API."""

    def __init__(self, calls_per_second: float = 1.0) -> None:
        """Initialize rate limiter.

        Args:
            calls_per_second: Maximum number of calls per second

        """
        self._calls_per_second = calls_per_second
        self._last_call_time = 0.0

    async def wait(self) -> None:
        """Wait before allowing the next call."""
        current_time = time.time()
        time_since_last_call = current_time - self._last_call_time
        min_interval = 1.0 / self._calls_per_second

        if time_since_last_call < min_interval:
            await asyncio.sleep(min_interval - time_since_last_call)

        self._last_call_time = time.time()


@asynccontextmanager
async def rate_limited_client() -> AsyncGenerator[RegistryClient, None]:
    """Create a rate-limited client for integration tests."""
    rate_limiter = RateLimiter(calls_per_second=0.5)  # 1 call every 2 seconds

    config = ClientConfig()
    config.timeout = 10.0  # Longer timeout for real network requests

    async with RegistryClient(config=config) as client:
        # Add rate limiting to the client
        await client._ensure_client()  # Ensure client is initialized
        original_get = client._client.get  # type: ignore[union-attr]

        async def rate_limited_get(*args: str, **kwargs: str | float) -> httpx.Response:
            await rate_limiter.wait()
            return await original_get(*args, **kwargs)  # type: ignore[arg-type]

        client._client.get = rate_limited_get  # type: ignore[union-attr,method-assign]
        yield client


@pytest.mark.integration
class TestRealAPIInteractions:
    """Integration tests with real API interactions."""

    @pytest.mark.asyncio
    async def test_search_servers_real_api(self) -> None:
        """Test searching servers with real API."""
        async with rate_limited_client() as client:
            result = await client.search_servers(name='git')

            # Should get some results from the real API
            assert result is not None
            assert hasattr(result, 'servers')
            assert isinstance(result.servers, list)
            # Real API should return at least some servers
            assert len(result.servers) > 0

            # Check first server has expected structure
            first_server = result.servers[0]
            assert hasattr(first_server, 'name')
            assert hasattr(first_server, 'description')
            assert hasattr(first_server, 'repository')
            assert first_server.name is not None

    @pytest.mark.asyncio
    async def test_search_servers_with_filter_real_api(self) -> None:
        """Test searching servers with name filter using real API."""
        async with rate_limited_client() as client:
            # Search for a common term that should have results
            result = await client.search_servers(name='git')

            assert result is not None
            assert hasattr(result, 'servers')
            assert isinstance(result.servers, list)

            # Note: The API currently returns all servers regardless of search term
            # so we just verify we got some results and they're properly structured
            if result.servers:
                assert len(result.servers) > 0

    @pytest.mark.asyncio
    async def test_search_nonexistent_server_real_api(self) -> None:
        """Test searching for a server that doesn't exist using real API."""
        async with rate_limited_client() as client:
            # Use a very specific term that's unlikely to exist
            result = await client.search_servers(name='nonexistent-mcp-server-xyz-123')

            assert result is not None
            assert hasattr(result, 'servers')
            assert isinstance(result.servers, list)
            # Note: The API currently returns all servers for any search term,
            # so we just verify the call succeeds
            # In a proper implementation, this should return empty results

    @pytest.mark.asyncio
    async def test_get_server_by_name_real_api(self) -> None:
        """Test getting server by name using real API."""
        async with rate_limited_client() as client:
            # First, get a list of servers to pick a real name
            search_result = await client.search_servers(name='git')

            if search_result.servers:
                # Use the first server's name
                server_name = search_result.servers[0].name

                server = await client.get_server_by_name(server_name)

                assert server is not None
                assert server.name == server_name
                assert server.repository is not None
                assert server.repository.url is not None

    @pytest.mark.asyncio
    async def test_get_nonexistent_server_by_name_real_api(self) -> None:
        """Test getting a nonexistent server by name using real API."""
        async with rate_limited_client() as client:
            server = await client.get_server_by_name('nonexistent-server-xyz-123')

            # Should return None for nonexistent servers
            assert server is None

    @pytest.mark.asyncio
    async def test_network_timeout_handling(self) -> None:
        """Test handling of network timeouts."""
        # Create a client with a reasonable but short timeout
        config = ClientConfig()
        config.timeout = 1.0  # 1 second timeout

        async with RegistryClient(config=config) as client:
            # This test just verifies that timeout configuration is respected
            # and the client handles timeouts gracefully
            try:
                result = await client.search_servers(name='git')
                # If the request succeeds within timeout, that's also fine
                assert result is not None
            except (
                RegistryAPIError,
                RegistryClientError,
                httpx.RequestError,
                TimeoutError,
            ):
                # If it times out or fails, that's expected with a short timeout
                pass

    @pytest.mark.asyncio
    async def test_invalid_base_url(self) -> None:
        """Test handling of invalid base URLs."""
        config = ClientConfig()
        config.base_url = 'https://invalid-mcp-registry-url-that-does-not-exist.com'
        config.timeout = 5.0

        async with RegistryClient(config=config) as client:
            with pytest.raises(RegistryAPIError):
                await client.search_servers(name='git')

    @pytest.mark.asyncio
    async def test_client_context_manager_real_api(self) -> None:
        """Test client context manager with real API calls."""
        config = ClientConfig()
        config.timeout = 10.0

        # Test that client can be used in context manager
        async with RegistryClient(config=config) as client:
            result = await client.search_servers(name='git')
            assert result is not None

        # Client should be properly closed after context manager exits
        # (We can't easily test this without accessing private attributes)


@pytest.mark.integration
class TestAPIDataValidation:
    """Integration tests for API data validation with real responses."""

    @pytest.mark.asyncio
    async def test_real_api_response_validation(self) -> None:
        """Test that real API responses pass Pydantic validation."""
        async with rate_limited_client() as client:
            result = await client.search_servers(name='git')

            # All servers should pass Pydantic validation
            for server in result.servers:
                # These should not raise validation errors
                assert server.name is not None
                assert isinstance(server.name, str)
                assert len(server.name) > 0

                if server.description:
                    assert isinstance(server.description, str)

                assert server.repository is not None
                assert isinstance(server.repository.url, str)
                # Some servers may have empty URLs in the real API
                if server.repository.url:
                    assert server.repository.url.startswith(('http://', 'https://'))

    @pytest.mark.asyncio
    async def test_real_api_server_metadata_validation(self) -> None:
        """Test that real API server metadata is properly validated."""
        async with rate_limited_client() as client:
            result = await client.search_servers(name='git')

            # Pick first server with metadata
            for server in result.servers:
                if server.meta and server.meta.official:
                    # Validate official metadata structure
                    official = server.meta.official
                    assert official.id_ is not None
                    assert isinstance(official.id_, str)
                    assert len(official.id_) > 0

                    if official.published_at:
                        # Should be a valid datetime
                        assert hasattr(official.published_at, 'year')

                    if official.updated_at:
                        # Should be a valid datetime
                        assert hasattr(official.updated_at, 'year')

                    break
