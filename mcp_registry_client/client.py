"""Async HTTP client for the MCP registry API."""

import logging
from typing import Any

import httpx
from pydantic import ValidationError

from .cache import ResponseCache
from .config import ClientConfig, get_client_config
from .models import RegistryError, SearchResponse, Server
from .retry import RetryStrategy, with_retry

logger = logging.getLogger(__name__)


class RegistryClientError(Exception):
    """Base exception for registry client errors."""


class RegistryAPIError(RegistryClientError):
    """Exception raised when the registry API returns an error."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        """Init.

        Takes
          - message: str - error message from registry API
          - status_code: int - status from registry API
        """
        self.status_code = status_code
        super().__init__(message)


class RegistryClient:
    """Async client for the MCP registry API."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float | None = None,
        config: ClientConfig | None = None,
    ) -> None:
        """Initialize the registry client.

        Args:
            base_url: Base URL for the registry API (overrides config)
            timeout: Request timeout in seconds (overrides config)
            config: Client configuration (if None, loads from environment)

        """
        if config is None:
            config = get_client_config(base_url=base_url, timeout=timeout)
        else:
            # Apply overrides to provided config
            if base_url is not None:
                config.base_url = base_url
            if timeout is not None:
                config.timeout = timeout

        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.timeout = config.timeout
        self._client: httpx.AsyncClient | None = None
        self._retry_strategy = RetryStrategy(config)
        self._cache = ResponseCache(config)

        # Create timeout configuration
        self._timeout_config = httpx.Timeout(
            connect=config.connect_timeout,
            read=config.read_timeout,
            write=config.write_timeout,
            pool=config.pool_timeout,
        )

    async def __aenter__(self) -> 'RegistryClient':
        """Async context manager entry."""
        await self._ensure_client()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Async context manager exit."""
        await self.close()

    async def _ensure_client(self) -> None:
        """Ensure the HTTP client is initialized."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self._timeout_config,
                headers={
                    'User-Agent': self.config.user_agent,
                    'Accept': 'application/json',
                },
            )

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _make_request(
        self,
        method: str,
        path: str,
        **kwargs: Any,  # noqa: ANN401,
    ) -> httpx.Response:
        """Make an HTTP request and handle errors.

        Args:
            method: HTTP method
            path: API path
            **kwargs: Additional arguments for the request

        Returns:
            HTTP response

        Raises:
            RegistryAPIError: If the API returns an error

        """
        await self._ensure_client()

        if self._client is None:
            msg = 'HTTP client not initialized'
            raise RegistryClientError(msg)

        async def _do_request() -> httpx.Response:
            if self._client is None:
                msg = 'HTTP client not initialized'
                raise RegistryClientError(msg)

            # Let retry logic handle exceptions
            response = await self._client.request(method, path, **kwargs)
            response.raise_for_status()
            return response

        # Use retry logic for the request
        operation_name = f'{method} {path}'
        try:
            return await with_retry(_do_request, self._retry_strategy, operation_name)
        except httpx.RequestError as e:
            logger.debug('Request error after retries: %s', e)
            msg = f'Request failed: {e}'
            raise RegistryAPIError(msg) from e
        except httpx.HTTPStatusError as e:
            logger.debug('HTTP error after retries: %s', e)
            # Try to parse error response
            try:
                error_data = e.response.json()
                error = RegistryError.model_validate(error_data)
                raise RegistryAPIError(
                    error.message or error.error,
                    status_code=e.response.status_code,
                ) from e
            except (ValueError, ValidationError):
                # Fallback to generic error message
                msg = f'HTTP {e.response.status_code}: {e.response.text}'
                raise RegistryAPIError(
                    msg,
                    status_code=e.response.status_code,
                ) from e

    async def search_servers(self, name: str) -> SearchResponse:
        """Search for MCP servers in the registry.

        Args:
            name: Name filter for servers (required to avoid returning hundreds of servers)

        Returns:
            Search response with list of servers matching the name filter

        Raises:
            RegistryAPIError: If the API request fails
            RegistryClientError: If response parsing fails

        """
        if not name or not name.strip():
            msg = 'Search term is required to avoid returning all servers'
            raise ValueError(msg)

        # Check cache first
        cache_key = self._cache.cache_key_for_search(name)
        cached_result = await self._cache.get(cache_key)
        if cached_result is not None:
            logger.debug('Returning cached search result for: %s', name)
            return cached_result  # type: ignore[no-any-return]

        params = {'search': name.strip()}
        logger.debug('Searching servers with params: %s', params)

        response = await self._make_request('GET', '/v0/servers', params=params)

        try:
            data = response.json()
            search_response = SearchResponse.model_validate(data)

            # Filter servers to only include those with active status
            active_servers = [
                server for server in search_response.servers if server.status == 'active'
            ]

            # Create filtered response
            result = SearchResponse(servers=active_servers)

            # Cache the result
            await self._cache.set(cache_key, result)
        except (ValueError, ValidationError) as e:
            logger.exception('Failed to parse search response: %s')
            msg = f'Failed to parse response: {e}'
            raise RegistryClientError(msg) from e
        else:
            return result

    async def get_server_by_id(self, server_id: str) -> Server | None:
        """Get a specific server by its ID.

        Args:
            server_id: The server ID from the registry

        Returns:
            Server details if the server is active, None otherwise

        Raises:
            RegistryAPIError: If the API request fails
            RegistryClientError: If response parsing fails

        """
        # Check cache first
        cache_key = self._cache.cache_key_for_server(server_id)
        cached_result = await self._cache.get(cache_key)
        if cached_result is not None:
            logger.debug('Returning cached server result for: %s', server_id)
            return cached_result  # type: ignore[no-any-return]

        logger.debug('Getting server with ID: %s', server_id)

        response = await self._make_request('GET', f'/v0/servers/{server_id}')
        data = response.json()
        retval = None
        try:
            server = Server.model_validate(data)

            # Only return server if it has active status
            if server.status == 'active':
                retval = server
            else:
                logger.debug(
                    'Server %s has status %s, filtering out', server_id, server.status
                )

            # Cache the result (even if None for inactive servers)
            await self._cache.set(cache_key, retval)

        except (ValueError, ValidationError) as e:
            logger.exception('Failed to parse server response: %s')
            msg = f'Failed to parse response: {e}'
            raise RegistryClientError(msg) from e

        return retval

    async def get_server_by_name(self, name: str) -> Server | None:
        """Get a server by its name.

        This method searches for servers, finds a match, and then fetches
        the full server details using the server ID. Only active servers are returned.

        Args:
            name: The server name to search for

        Returns:
            Server details if found and active, None otherwise

        Raises:
            RegistryAPIError: If the API request fails

        """
        # Check cache first
        cache_key = self._cache.cache_key_for_server_by_name(name)
        cached_result = await self._cache.get(cache_key)
        if cached_result is not None:
            logger.debug('Returning cached server by name result for: %s', name)
            return cached_result  # type: ignore[no-any-return]

        logger.debug('Getting server with name: %s', name)

        # Search for servers with the given name (already filtered to active)
        search_result = await self.search_servers(name=name)

        # Find exact match first
        server_id = None
        for server in search_result.servers:
            if server.name == name:
                server_id = server.meta.official.id_
                break

        # If no exact match, try to find partial match
        if server_id is None:
            for server in search_result.servers:
                if name.lower() in server.name.lower():
                    server_id = server.meta.official.id_
                    break

        # If we found a server, get its full details by ID
        retval = None
        if server_id:
            # get_server_by_id already filters for active status
            retval = await self.get_server_by_id(server_id)

        # Cache the result (even if None)
        await self._cache.set(cache_key, retval)

        return retval
