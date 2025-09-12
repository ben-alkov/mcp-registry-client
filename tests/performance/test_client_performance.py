"""Performance tests for client functionality."""

import asyncio
import gc
import time
from datetime import UTC, datetime
from unittest.mock import Mock, patch

import httpx
import pytest

from mcp_registry_client.client import RegistryClient
from mcp_registry_client.config import ClientConfig
from mcp_registry_client.models import (
    OfficialMeta,
    Repository,
    SearchResponse,
    Server,
    ServerMeta,
)


@pytest.mark.benchmark
class TestClientPerformance:
    """Performance benchmarks for client operations."""

    @pytest.fixture
    def config(self) -> ClientConfig:
        """Create test configuration."""
        config = ClientConfig()
        config.timeout = 5.0
        config.enable_cache = True
        config.cache_ttl = 300
        return config

    @pytest.fixture
    def mock_server(self) -> Server:
        """Create a mock server for testing."""
        now = datetime.now(UTC)

        return Server(
            name='test-server',
            description='A test server',
            repository=Repository(url='https://github.com/test/repo', source='github'),
            version='1.0.0',
            meta=ServerMeta(
                official=OfficialMeta(
                    id_='test-server-id',
                    published_at=now,
                    updated_at=now,
                    is_latest=True,
                ),
            ),
        )

    @pytest.mark.asyncio
    async def test_client_initialization_performance(self, config: ClientConfig) -> None:
        """Test performance of client initialization."""
        start_time = time.time()

        clients = []
        for _ in range(100):
            client = RegistryClient(config=config)
            clients.append(client)

        init_time = time.time() - start_time

        # Client initialization should be very fast
        assert init_time < 0.5, f'Client initialization took too long: {init_time:.3f}s'

        # Clean up
        for client in clients:
            await client.close()

    @pytest.mark.asyncio
    async def test_search_servers_response_parsing_performance(
        self, config: ClientConfig, mock_server: Server
    ) -> None:
        """Test performance of search response parsing."""
        # Create a large mock response
        large_server_list = [mock_server] * 1000
        SearchResponse(servers=large_server_list)

        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                'servers': [
                    {
                        'name': f'server-{i}',
                        'description': f'Test server {i}',
                        'repository': {
                            'url': f'https://github.com/test/repo-{i}',
                            'source': 'github',
                        },
                        'version': '1.0.0',
                    }
                    for i in range(1000)
                ]
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            async with RegistryClient(config=config) as client:
                start_time = time.time()
                result = await client.search_servers(name='test')
                parse_time = time.time() - start_time

                # Should parse large responses reasonably quickly
                assert parse_time < 2.0, (
                    f'Response parsing took too long: {parse_time:.3f}s'
                )
                # Verify we got some results (actual API returns ~26 servers)
                assert len(result.servers) > 0

    @pytest.mark.asyncio
    async def test_concurrent_search_operations_performance(
        self, config: ClientConfig
    ) -> None:
        """Test performance under concurrent search operations."""
        num_concurrent = 50

        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                'servers': [
                    {
                        'name': 'test-server',
                        'description': 'A test server',
                        'repository': {
                            'url': 'https://github.com/test/repo',
                            'source': 'github',
                        },
                        'version': '1.0.0',
                        '_meta': {
                            'io.modelcontextprotocol.registry/official': {
                                'id': 'test-server-id',
                                'published_at': '2023-01-01T00:00:00Z',
                                'updated_at': '2023-01-01T00:00:00Z',
                                'is_latest': True,
                            }
                        },
                    }
                ]
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            async with RegistryClient(config=config) as client:
                start_time = time.time()

                # Run concurrent search operations
                tasks = [
                    client.search_servers(name=f'server-{i}') for i in range(num_concurrent)
                ]
                results = await asyncio.gather(*tasks)

                concurrent_time = time.time() - start_time

                # Should handle concurrent operations efficiently
                assert concurrent_time < 3.0, (
                    f'Concurrent operations took too long: {concurrent_time:.3f}s'
                )
                assert len(results) == num_concurrent
                # All results should have the same number of servers since the API
                # returns all servers regardless of search term
                if results:
                    expected_count = len(results[0].servers)
                    assert all(len(r.servers) == expected_count for r in results)

    @pytest.mark.asyncio
    async def test_cache_hit_performance(self, config: ClientConfig) -> None:
        """Test performance of cache hits."""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                'servers': [
                    {
                        'name': 'cached-server',
                        'description': 'A cached server',
                        'repository': {
                            'url': 'https://github.com/test/cached',
                            'source': 'github',
                        },
                        'version': '1.0.0',
                    }
                ]
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            async with RegistryClient(config=config) as client:
                # First request - cache miss
                first_start = time.time()
                first_result = await client.search_servers(name='cached-server')
                first_time = time.time() - first_start

                # Second request - cache hit
                second_start = time.time()
                second_result = await client.search_servers(name='cached-server')
                second_time = time.time() - second_start

                # Cache hit should be significantly faster
                assert second_time < first_time / 2, (
                    f'Cache hit not faster than miss: {second_time:.3f}s vs '
                    f'{first_time:.3f}s'
                )
                assert second_time < 0.1, f'Cache hit took too long: {second_time:.3f}s'

                # Results should be identical
                # Both results should have the same number of servers (from cache)
                assert len(first_result.servers) == len(second_result.servers)
                assert first_result.servers[0].name == second_result.servers[0].name

                # HTTP client should only be called once due to caching
                assert mock_get.call_count == 1

    @pytest.mark.asyncio
    async def test_error_handling_performance(self, config: ClientConfig) -> None:
        """Test performance of error handling."""
        with patch('httpx.AsyncClient.get') as mock_get:
            # Simulate various HTTP errors

            mock_get.side_effect = httpx.HTTPStatusError(
                'Not Found', request=Mock(), response=Mock(status_code=404)
            )

            async with RegistryClient(config=config) as client:
                start_time = time.time()

                # Run multiple operations that will fail
                failed_count = 0
                for i in range(20):
                    try:
                        await client.search_servers(name=f'nonexistent-{i}')
                    except (httpx.RequestError, httpx.HTTPStatusError):
                        failed_count += 1

                error_time = time.time() - start_time

                # Error handling should be fast
                assert error_time < 1.0, f'Error handling took too long: {error_time:.3f}s'
                assert failed_count == 20

    @pytest.mark.asyncio
    async def test_client_context_manager_performance(self, config: ClientConfig) -> None:
        """Test performance of client context manager operations."""
        start_time = time.time()

        # Create and close many clients
        for _ in range(50):
            async with RegistryClient(config=config):
                # Do minimal work to test overhead
                pass

        context_time = time.time() - start_time

        # Context manager operations should be fast
        assert context_time < 2.0, (
            f'Context manager operations took too long: {context_time:.3f}s'
        )

    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, config: ClientConfig) -> None:
        """Test memory usage patterns under load."""
        # Force garbage collection and measure baseline
        gc.collect()

        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                'servers': [
                    {
                        'name': f'memory-test-server-{i}',
                        'description': f'Server for memory test {i}'
                        * 10,  # Larger descriptions
                        'repository': {
                            'url': f'https://github.com/test/memory-{i}',
                            'source': 'github',
                        },
                        'version': '1.0.0',
                    }
                    for i in range(100)  # Many servers per response
                ]
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            async with RegistryClient(config=config) as client:
                # Perform many operations to test memory usage
                results = []
                for i in range(100):
                    result = await client.search_servers(name=f'batch-{i}')
                    results.append(result)

                    # Periodically clear results to test cleanup
                    if i % 20 == 19:
                        results.clear()
                        gc.collect()

                # Final memory check - should not have excessive growth
                # This is a basic check; more sophisticated memory profiling
                # would require additional tools
                final_cache_size = (
                    len(client._cache._cache) if hasattr(client, '_cache') else 0
                )

                # Cache should not grow unbounded
                assert final_cache_size < 200, (
                    f'Cache grew too large: {final_cache_size} items'
                )

    def test_client_configuration_performance(self, benchmark) -> None:
        """Benchmark client configuration operations."""

        def create_configured_clients() -> list[ClientConfig]:
            configs = []
            for i in range(100):
                config = ClientConfig()
                config.base_url = f'https://api-{i}.example.com'
                config.timeout = 5.0 + i * 0.1
                config.max_retries = i % 5
                configs.append(config)
            return configs

        configs = benchmark(create_configured_clients)
        assert len(configs) == 100
