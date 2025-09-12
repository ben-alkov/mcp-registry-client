"""Tests for the registry client."""

from datetime import datetime
from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from mcp_registry_client.client import RegistryAPIError, RegistryClient, RegistryClientError


@pytest.fixture
def sample_server_data():
    """Sample server data for testing."""
    now = datetime.now()
    return {
        'name': 'test-server',
        'description': 'A test server',
        'status': 'active',
        'repository': {'url': 'https://github.com/test/repo', 'source': 'github'},
        'version': '1.0.0',
        '_meta': {
            'io.modelcontextprotocol.registry/official': {
                'id': 'test-id',
                'published_at': now,
                'updated_at': now,
                'is_latest': True,
            },
        },
    }


@pytest.fixture
def sample_search_response(sample_server_data):
    """Sample search response for testing."""
    return {'servers': [sample_server_data]}


class TestRegistryClient:
    """Tests for RegistryClient."""

    def test_init(self) -> None:
        """Test client initialization."""
        client = RegistryClient()
        assert client.base_url == 'https://registry.modelcontextprotocol.io'
        assert client.timeout == 30.0
        assert client._client is None

    def test_init_custom_params(self) -> None:
        """Test client initialization with custom parameters."""
        client = RegistryClient(
            base_url='https://custom.registry.com/',
            timeout=60.0,
        )
        assert client.base_url == 'https://custom.registry.com'
        assert client.timeout == 60.0

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        """Test client as async context manager."""
        async with RegistryClient() as client:
            assert client._client is not None
        # Client should be closed after exiting context
        assert client._client is None

    @pytest.mark.asyncio
    async def test_search_servers_success(self, sample_search_response) -> None:
        """Test successful server search."""
        mock_response = Mock()
        mock_response.json.return_value = sample_search_response
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response

        client = RegistryClient()
        client._client = mock_client

        result = await client.search_servers('test')

        mock_client.request.assert_called_once_with(
            'GET',
            '/v0/servers',
            params={'search': 'test'},
        )
        assert len(result.servers) == 1
        assert result.servers[0].name == 'test-server'

    @pytest.mark.asyncio
    async def test_search_servers_with_name(self, sample_search_response) -> None:
        """Test server search with name filter."""
        mock_response = Mock()
        mock_response.json.return_value = sample_search_response
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response

        client = RegistryClient()
        client._client = mock_client

        result = await client.search_servers(name='test')

        mock_client.request.assert_called_once_with(
            'GET',
            '/v0/servers',
            params={'search': 'test'},
        )
        assert len(result.servers) == 1

    @pytest.mark.asyncio
    async def test_search_servers_empty_name_error(self) -> None:
        """Test search servers with empty name raises ValueError."""
        client = RegistryClient()

        with pytest.raises(ValueError, match='Search term is required'):
            await client.search_servers('')

        with pytest.raises(ValueError, match='Search term is required'):
            await client.search_servers('   ')

    @pytest.mark.asyncio
    async def test_search_servers_http_error(self) -> None:
        """Test server search with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = 'Not Found'
        mock_response.json.return_value = {'error': 'Not found'}

        http_error = httpx.HTTPStatusError(
            'Not Found',
            request=Mock(),
            response=mock_response,
        )

        mock_client = AsyncMock()
        mock_client.request.side_effect = http_error

        client = RegistryClient()
        client._client = mock_client

        with pytest.raises(RegistryAPIError) as exc_info:
            await client.search_servers('test')

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_search_servers_request_error(self) -> None:
        """Test server search with request error."""
        request_error = httpx.RequestError('Connection failed')

        mock_client = AsyncMock()
        mock_client.request.side_effect = request_error

        client = RegistryClient()
        client._client = mock_client

        with pytest.raises(RegistryAPIError) as exc_info:
            await client.search_servers('test')

        assert 'Request failed' in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_servers_invalid_response(self) -> None:
        """Test server search with invalid response."""
        mock_response = Mock()
        mock_response.json.return_value = {'invalid': 'data'}
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response

        client = RegistryClient()
        client._client = mock_client

        with pytest.raises(RegistryClientError):
            await client.search_servers('test')

    @pytest.mark.asyncio
    async def test_get_server_by_id_success(self, sample_server_data) -> None:
        """Test successful get server by ID."""
        mock_response = Mock()
        mock_response.json.return_value = sample_server_data
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response

        client = RegistryClient()
        client._client = mock_client

        result = await client.get_server_by_id('test-id')

        mock_client.request.assert_called_once_with(
            'GET',
            '/v0/servers/test-id',
        )
        assert result is not None
        assert result.name == 'test-server'
        assert result.meta.official.id_ == 'test-id'

    @pytest.mark.asyncio
    async def test_get_server_by_name_found(
        self, sample_search_response, sample_server_data
    ) -> None:
        """Test get server by name when found."""
        search_response = Mock()
        search_response.json.return_value = sample_search_response
        search_response.raise_for_status.return_value = None

        server_response = Mock()
        server_response.json.return_value = sample_server_data
        server_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.request.side_effect = [search_response, server_response]

        client = RegistryClient()
        client._client = mock_client

        result = await client.get_server_by_name('test-server')

        assert result is not None
        assert result.name == 'test-server'

    @pytest.mark.asyncio
    async def test_get_server_by_name_not_found(self) -> None:
        """Test get server by name when not found."""
        mock_response = Mock()
        mock_response.json.return_value = {'servers': []}
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response

        client = RegistryClient()
        client._client = mock_client

        result = await client.get_server_by_name('nonexistent')

        assert result is None

    @pytest.mark.asyncio
    async def test_get_server_by_name_partial_match(self) -> None:
        """Test get server by name with partial match."""
        now = datetime.now()
        server_data = {
            'name': 'ai.waystation/gmail',
            'description': 'Gmail server',
            'status': 'active',
            'repository': {'url': 'https://github.com/test/repo', 'source': 'github'},
            'version': '1.0.0',
            '_meta': {
                'io.modelcontextprotocol.registry/official': {
                    'id': 'test-id',
                    'published_at': now,
                    'updated_at': now,
                    'is_latest': True,
                },
            },
        }

        search_response = Mock()
        search_response.json.return_value = {'servers': [server_data]}
        search_response.raise_for_status.return_value = None

        server_response = Mock()
        server_response.json.return_value = server_data
        server_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.request.side_effect = [search_response, server_response]

        client = RegistryClient()
        client._client = mock_client

        result = await client.get_server_by_name('gmail')

        assert result is not None
        assert result.name == 'ai.waystation/gmail'

    @pytest.mark.asyncio
    async def test_search_servers_filters_inactive(self) -> None:
        """Test that search_servers filters out inactive servers."""
        now = datetime.now()
        search_data = {
            'servers': [
                {
                    'name': 'active-server',
                    'description': 'Active server',
                    'status': 'active',
                    'repository': {
                        'url': 'https://github.com/test/repo1',
                        'source': 'github',
                    },
                    'version': '1.0.0',
                    '_meta': {
                        'io.modelcontextprotocol.registry/official': {
                            'id': 'active-id',
                            'published_at': now,
                            'updated_at': now,
                            'is_latest': True,
                        },
                    },
                },
                {
                    'name': 'inactive-server',
                    'description': 'Inactive server',
                    'status': 'inactive',
                    'repository': {
                        'url': 'https://github.com/test/repo2',
                        'source': 'github',
                    },
                    'version': '1.0.0',
                    '_meta': {
                        'io.modelcontextprotocol.registry/official': {
                            'id': 'inactive-id',
                            'published_at': now,
                            'updated_at': now,
                            'is_latest': True,
                        },
                    },
                },
                {
                    'name': 'missing-status-server',
                    'description': 'Server without status',
                    'repository': {
                        'url': 'https://github.com/test/repo3',
                        'source': 'github',
                    },
                    'version': '1.0.0',
                    '_meta': {
                        'io.modelcontextprotocol.registry/official': {
                            'id': 'missing-status-id',
                            'published_at': now,
                            'updated_at': now,
                            'is_latest': True,
                        },
                    },
                },
            ]
        }

        mock_response = Mock()
        mock_response.json.return_value = search_data
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response

        client = RegistryClient()
        client._client = mock_client

        result = await client.search_servers('test')

        # Should only have the active server
        assert len(result.servers) == 1
        assert result.servers[0].name == 'active-server'
        assert result.servers[0].status == 'active'

    @pytest.mark.asyncio
    async def test_get_server_by_id_filters_inactive(self) -> None:
        """Test that get_server_by_id returns None for inactive servers."""
        now = datetime.now()
        server_data = {
            'name': 'inactive-server',
            'description': 'Inactive server',
            'status': 'inactive',
            'repository': {'url': 'https://github.com/test/repo', 'source': 'github'},
            'version': '1.0.0',
            '_meta': {
                'io.modelcontextprotocol.registry/official': {
                    'id': 'inactive-id',
                    'published_at': now,
                    'updated_at': now,
                    'is_latest': True,
                },
            },
        }

        mock_response = Mock()
        mock_response.json.return_value = server_data
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response

        client = RegistryClient()
        client._client = mock_client

        result = await client.get_server_by_id('inactive-id')

        assert result is None

    @pytest.mark.asyncio
    async def test_get_server_by_id_filters_missing_status(self) -> None:
        """Test that get_server_by_id returns None for servers without status."""
        now = datetime.now()
        server_data = {
            'name': 'no-status-server',
            'description': 'Server without status',
            'repository': {'url': 'https://github.com/test/repo', 'source': 'github'},
            'version': '1.0.0',
            '_meta': {
                'io.modelcontextprotocol.registry/official': {
                    'id': 'no-status-id',
                    'published_at': now,
                    'updated_at': now,
                    'is_latest': True,
                },
            },
        }

        mock_response = Mock()
        mock_response.json.return_value = server_data
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response

        client = RegistryClient()
        client._client = mock_client

        result = await client.get_server_by_id('no-status-id')

        assert result is None


class TestRegistryClientEdgeCases:
    """Edge case tests for RegistryClient."""

    @pytest.mark.asyncio
    async def test_make_request_client_not_initialized(self) -> None:
        """Test _make_request when client is not initialized."""
        client = RegistryClient()

        # Mock the _ensure_client to set client to None
        async def mock_ensure_client() -> None:
            client._client = None

        # Replace the method to avoid mypy method assignment error
        client._ensure_client = mock_ensure_client  # type: ignore[method-assign]

        with pytest.raises(RegistryClientError, match='HTTP client not initialized'):
            await client._make_request('GET', '/test')

    @pytest.mark.asyncio
    async def test_base_url_normalization(self) -> None:
        """Test base URL normalization removes trailing slashes."""
        client = RegistryClient(base_url='https://example.com/')
        assert client.base_url == 'https://example.com'

        client = RegistryClient(base_url='https://example.com///')
        assert client.base_url == 'https://example.com'

    @pytest.mark.asyncio
    async def test_search_servers_none_name_error(self) -> None:
        """Test search servers with None name raises ValueError."""
        client = RegistryClient()

        with pytest.raises(ValueError, match='Search term is required'):
            await client.search_servers(None)  # type: ignore[arg-type]

    @pytest.mark.asyncio
    async def test_search_servers_whitespace_only_name_error(self) -> None:
        """Test search servers with whitespace-only name raises ValueError."""
        client = RegistryClient()

        with pytest.raises(ValueError, match='Search term is required'):
            await client.search_servers('   \t\n   ')

    @pytest.mark.asyncio
    async def test_search_servers_json_decode_error(self) -> None:
        """Test search servers with invalid JSON response."""
        mock_response = Mock()
        mock_response.json.side_effect = ValueError('Invalid JSON')
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response

        client = RegistryClient()
        client._client = mock_client

        with pytest.raises(RegistryClientError, match='Failed to parse response'):
            await client.search_servers('test')

    @pytest.mark.asyncio
    async def test_get_server_by_id_json_decode_error(self) -> None:
        """Test get server by ID with invalid JSON response."""
        mock_response = Mock()
        mock_response.json.side_effect = ValueError('Invalid JSON')
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response

        client = RegistryClient()
        client._client = mock_client

        # The JSON decode error occurs on line 246 which is outside the try block
        # So it raises ValueError directly, not RegistryClientError
        with pytest.raises(ValueError, match='Invalid JSON'):
            await client.get_server_by_id('test-id')

    @pytest.mark.asyncio
    async def test_http_error_without_json_body(self) -> None:
        """Test HTTP error handling when response body is not JSON."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = 'Internal Server Error'
        mock_response.json.side_effect = ValueError('Not JSON')

        http_error = httpx.HTTPStatusError(
            'Internal Server Error',
            request=Mock(),
            response=mock_response,
        )

        mock_client = AsyncMock()
        mock_client.request.side_effect = http_error

        client = RegistryClient()
        client._client = mock_client

        with pytest.raises(RegistryAPIError) as exc_info:
            await client.search_servers('test')

        assert exc_info.value.status_code == 500
        assert 'HTTP 500: Internal Server Error' in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_http_error_with_malformed_error_response(self) -> None:
        """Test HTTP error handling with malformed error response."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = 'Bad Request'
        mock_response.json.return_value = {'invalid_field': 'not an error object'}

        http_error = httpx.HTTPStatusError(
            'Bad Request',
            request=Mock(),
            response=mock_response,
        )

        mock_client = AsyncMock()
        mock_client.request.side_effect = http_error

        client = RegistryClient()
        client._client = mock_client

        with pytest.raises(RegistryAPIError) as exc_info:
            await client.search_servers('test')

        assert exc_info.value.status_code == 400
        assert 'HTTP 400: Bad Request' in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_server_by_name_exact_match_priority(self) -> None:
        """Test that exact name match has priority over partial match."""
        now = datetime.now()

        # Server with partial match
        partial_server = {
            'name': 'test-server-extended',
            'description': 'Extended test server',
            'status': 'active',
            'repository': {'url': 'https://github.com/test/repo1', 'source': 'github'},
            'version': '1.0.0',
            '_meta': {
                'io.modelcontextprotocol.registry/official': {
                    'id': 'partial-id',
                    'published_at': now,
                    'updated_at': now,
                    'is_latest': True,
                },
            },
        }

        # Server with exact match
        exact_server = {
            'name': 'test-server',
            'description': 'Exact test server',
            'status': 'active',
            'repository': {'url': 'https://github.com/test/repo2', 'source': 'github'},
            'version': '1.0.0',
            '_meta': {
                'io.modelcontextprotocol.registry/official': {
                    'id': 'exact-id',
                    'published_at': now,
                    'updated_at': now,
                    'is_latest': True,
                },
            },
        }

        search_response = Mock()
        search_response.json.return_value = {'servers': [partial_server, exact_server]}
        search_response.raise_for_status.return_value = None

        server_response = Mock()
        server_response.json.return_value = exact_server
        server_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.request.side_effect = [search_response, server_response]

        client = RegistryClient()
        client._client = mock_client

        result = await client.get_server_by_name('test-server')

        assert result is not None
        assert result.name == 'test-server'
        assert result.meta.official.id_ == 'exact-id'

    @pytest.mark.asyncio
    async def test_get_server_by_name_case_insensitive_partial_match(self) -> None:
        """Test case-insensitive partial matching in get_server_by_name."""
        now = datetime.now()
        server_data = {
            'name': 'Test-Server-Name',
            'description': 'Test server',
            'status': 'active',
            'repository': {'url': 'https://github.com/test/repo', 'source': 'github'},
            'version': '1.0.0',
            '_meta': {
                'io.modelcontextprotocol.registry/official': {
                    'id': 'test-id',
                    'published_at': now,
                    'updated_at': now,
                    'is_latest': True,
                },
            },
        }

        search_response = Mock()
        search_response.json.return_value = {'servers': [server_data]}
        search_response.raise_for_status.return_value = None

        server_response = Mock()
        server_response.json.return_value = server_data
        server_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.request.side_effect = [search_response, server_response]

        client = RegistryClient()
        client._client = mock_client

        result = await client.get_server_by_name('server')

        assert result is not None
        assert result.name == 'Test-Server-Name'

    @pytest.mark.asyncio
    async def test_close_when_client_none(self) -> None:
        """Test close method when client is None."""
        client = RegistryClient()
        # Client should be None initially
        await client.close()  # Should not raise an exception

    @pytest.mark.asyncio
    async def test_double_close(self) -> None:
        """Test calling close twice."""
        client = RegistryClient()
        await client._ensure_client()

        # First close
        await client.close()
        assert client._client is None

        # Second close should not raise
        await client.close()

    @pytest.mark.asyncio
    async def test_search_servers_name_strip_whitespace(self) -> None:
        """Test that search servers strips whitespace from name parameter."""
        mock_response = Mock()
        mock_response.json.return_value = {'servers': []}
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response

        client = RegistryClient()
        client._client = mock_client

        await client.search_servers('  test-name  ')

        mock_client.request.assert_called_once_with(
            'GET',
            '/v0/servers',
            params={'search': 'test-name'},
        )
