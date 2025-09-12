"""Tests for the CLI module."""

import json
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from mcp_registry_client.cli import (
    async_main,
    main,
)
from mcp_registry_client.client import RegistryAPIError, RegistryClientError
from mcp_registry_client.error_handling import handle_command_error
from mcp_registry_client.formatters import (
    format_env_variables,
    format_package_info,
    format_remotes,
    format_server_detailed,
    format_server_summary,
    print_json,
    print_table,
)
from mcp_registry_client.models import (
    EnvironmentVariable,
    OfficialMeta,
    Package,
    Remote,
    Repository,
    Server,
    ServerMeta,
    Transport,
)


@pytest.fixture
def sample_server():
    """Sample server for testing."""
    now = datetime.now()
    return Server(
        name='test-server',
        description='A test server for testing purposes',
        status='active',
        repository=Repository(url='https://github.com/test/repo', source='github'),
        version='1.0.0',
        meta=ServerMeta(
            official=OfficialMeta(
                id_='test-id',
                published_at=now,
                updated_at=now,
                is_latest=True,
            ),
        ),
    )


class TestFormatting:
    """Tests for formatting functions."""

    def test_format_server_summary(self, sample_server) -> None:
        """Test server summary formatting."""
        result = format_server_summary(sample_server)

        assert result['name'] == 'test-server'
        assert result['description'] == 'A test server for testing purposes'
        assert result['version'] == '1.0.0'
        assert result['status'] == 'active'
        assert result['repository'] == 'https://github.com/test/repo'
        assert result['id'] == 'test-id'
        assert 'published_at' in result
        assert 'updated_at' in result

    def test_format_server_detailed(self, sample_server) -> None:
        """Test detailed server formatting."""
        result = format_server_detailed(sample_server)

        assert result['name'] == 'test-server'
        assert result['description'] == 'A test server for testing purposes'
        assert result['version'] == '1.0.0'
        assert result['status'] == 'active'
        assert result['repository']['url'] == 'https://github.com/test/repo'
        assert result['repository']['source'] == 'github'
        assert result['metadata']['id'] == 'test-id'
        assert result['metadata']['is_latest'] is True

    def test_format_server_summary_missing_status(self) -> None:
        """Test server summary formatting with missing status."""
        now = datetime.now()
        server = Server(
            name='test-server',
            description='A test server for testing purposes',
            status=None,  # Missing status
            repository=Repository(url='https://github.com/test/repo', source='github'),
            version='1.0.0',
            meta=ServerMeta(
                official=OfficialMeta(
                    id_='test-id',
                    published_at=now,
                    updated_at=now,
                    is_latest=True,
                ),
            ),
        )

        result = format_server_summary(server)
        assert result['status'] == 'unknown'

    def test_format_server_detailed_missing_status(self) -> None:
        """Test detailed server formatting with missing status."""
        now = datetime.now()
        server = Server(
            name='test-server',
            description='A test server for testing purposes',
            status=None,  # Missing status
            repository=Repository(url='https://github.com/test/repo', source='github'),
            version='1.0.0',
            meta=ServerMeta(
                official=OfficialMeta(
                    id_='test-id',
                    published_at=now,
                    updated_at=now,
                    is_latest=True,
                ),
            ),
        )

        result = format_server_detailed(server)
        assert result['status'] == 'unknown'

    def test_print_json(self, capsys) -> None:
        """Test JSON printing."""
        data = {'test': 'value', 'number': 42}
        print_json(data)

        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed == data

    def test_print_table_empty(self, capsys) -> None:
        """Test table printing with empty list."""
        print_table([])

        captured = capsys.readouterr()
        assert 'No servers found.' in captured.out

    def test_print_table_with_servers(self, sample_server, capsys) -> None:
        """Test table printing with servers."""
        print_table([sample_server])

        captured = capsys.readouterr()
        output = captured.out

        assert 'NAME' in output
        assert 'VERSION' in output
        assert 'DESCRIPTION' in output
        assert 'test-server' in output
        assert '1.0.0' in output
        assert 'A test server for testing purposes' in output

    def test_format_env_variables_empty(self) -> None:
        """Test environment variables formatting with empty list."""
        package = Package(
            registry_type='npm',
            identifier='test-package',
            version='1.0.0',
        )
        result = format_env_variables(package)
        assert result == []

    def test_format_env_variables_with_data(self) -> None:
        """Test environment variables formatting with data."""
        env_var = EnvironmentVariable(
            name='API_KEY',
            description='API key for service',
            is_required=True,
            is_secret=True,
            format_='string',
        )
        package = Package(
            registry_type='npm',
            identifier='test-package',
            version='1.0.0',
            environment_variables=[env_var],
        )

        result = format_env_variables(package)

        assert len(result) == 1
        assert result[0]['name'] == 'API_KEY'
        assert result[0]['description'] == 'API key for service'
        assert result[0]['is_required'] is True
        assert result[0]['is_secret'] is True
        assert result[0]['format'] == 'string'

    def test_format_package_info_minimal(self) -> None:
        """Test package formatting with minimal data."""
        package = Package(
            registry_type='npm',
            identifier='test-package',
            version='1.0.0',
        )

        result = format_package_info(package)

        assert result['registry_type'] == 'npm'
        assert result['identifier'] == 'test-package'
        assert result['version'] == '1.0.0'
        assert 'registry_base_url' not in result
        assert 'runtime_hint' not in result
        assert 'transport' not in result
        assert 'environment_variables' not in result

    def test_format_package_info_full(self) -> None:
        """Test package formatting with full data."""
        transport = Transport(type_='http', url='http://test.com')
        env_var = EnvironmentVariable(
            name='TEST_VAR',
            description='Test variable',
            is_required=False,
            is_secret=False,
            format_='string',
        )
        package = Package(
            registry_type='npm',
            identifier='test-package',
            version='1.0.0',
            registry_base_url='https://registry.npmjs.org',
            runtime_hint='node',
            transport=transport,
            environment_variables=[env_var],
        )

        result = format_package_info(package)

        assert result['registry_base_url'] == 'https://registry.npmjs.org/'
        assert result['runtime_hint'] == 'node'
        assert result['transport']['type'] == 'http'
        assert result['transport']['url'] == 'http://test.com'
        assert len(result['environment_variables']) == 1
        assert result['environment_variables'][0]['name'] == 'TEST_VAR'

    def test_format_remotes(self) -> None:
        """Test remotes formatting."""
        remotes = [
            Remote(type_='git', url='https://github.com/test/repo.git'),
            Remote(type_='https', url='https://test.com/image'),
        ]

        result = format_remotes(remotes)

        assert len(result) == 2
        assert result[0]['type'] == 'git'
        assert result[0]['url'] == 'https://github.com/test/repo.git'
        assert result[1]['type'] == 'https'
        assert result[1]['url'] == 'https://test.com/image'

    def test_handle_command_error_api_error(self, capsys) -> None:
        """Test error handling for API errors."""
        exc = RegistryAPIError('API failed')
        exc.status_code = 404

        result = handle_command_error(exc, 'test operation')

        captured = capsys.readouterr()
        assert result == 1
        assert 'Error: Server not found (test operation)' in captured.err

    def test_handle_command_error_client_error(self, capsys) -> None:
        """Test error handling for client errors."""
        exc = RegistryClientError('Client failed')

        result = handle_command_error(exc, 'test operation')

        captured = capsys.readouterr()
        assert result == 1
        assert 'Error: Failed to process response (test operation)' in captured.err

    def test_handle_command_error_unexpected(self, capsys) -> None:
        """Test error handling for unexpected errors."""
        exc = ValueError('Something went wrong')

        result = handle_command_error(exc, 'test operation')

        captured = capsys.readouterr()
        assert result == 1
        assert 'Error: Unexpected error occurred (test operation)' in captured.err

    def test_handle_command_error_api_error_server_unavailable(self, capsys) -> None:
        """Test error handling for server unavailable (HTTP 500+)."""
        exc = RegistryAPIError('Internal server error')
        exc.status_code = 500

        result = handle_command_error(exc)

        captured = capsys.readouterr()
        assert result == 1
        assert (
            'Error: Registry service unavailable. Please try again later.' in captured.err
        )

    def test_handle_command_error_api_error_no_status_code(self, capsys) -> None:
        """Test error handling for API error without status code."""
        exc = RegistryAPIError('Network error')
        # Don't set status_code to test hasattr path

        result = handle_command_error(exc, 'network operation')

        captured = capsys.readouterr()
        assert result == 1
        assert 'Error: API request failed (network operation)' in captured.err


class TestCLI:
    """Tests for CLI functions."""

    @pytest.mark.asyncio
    async def test_search_command_success(self, sample_server) -> None:
        """Test successful search command."""
        mock_result = Mock()
        mock_result.servers = [sample_server]

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.search_servers.return_value = mock_result

        with (
            patch(
                'mcp_registry_client.commands.search.RegistryClient',
                return_value=mock_client,
            ),
            patch('sys.argv', ['mcp-registry', 'search', 'test']),
        ):
            result = await async_main()

        mock_client.search_servers.assert_called_once_with(name='test')
        assert result == 0

    @pytest.mark.asyncio
    async def test_search_command_with_name(self, sample_server) -> None:
        """Test search command with name filter."""
        mock_result = Mock()
        mock_result.servers = [sample_server]

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.search_servers.return_value = mock_result

        with (
            patch(
                'mcp_registry_client.commands.search.RegistryClient',
                return_value=mock_client,
            ),
            patch('sys.argv', ['mcp-registry', 'search', 'test']),
        ):
            result = await async_main()

        mock_client.search_servers.assert_called_once_with(name='test')
        assert result == 0

    @pytest.mark.asyncio
    async def test_search_command_json_output(self, sample_server, capsys) -> None:
        """Test search command with JSON output."""
        mock_result = Mock()
        mock_result.servers = [sample_server]

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.search_servers.return_value = mock_result

        with (
            patch(
                'mcp_registry_client.commands.search.RegistryClient',
                return_value=mock_client,
            ),
            patch('sys.argv', ['mcp-registry', '--json', 'search', 'test']),
        ):
            result = await async_main()

        assert result == 0

        captured = capsys.readouterr()
        output_data = json.loads(captured.out)
        assert len(output_data) == 1
        assert output_data[0]['name'] == 'test-server'

    @pytest.mark.asyncio
    async def test_info_command_success(self, sample_server) -> None:
        """Test successful info command."""
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get_server_by_name.return_value = sample_server

        with (
            patch(
                'mcp_registry_client.commands.info.RegistryClient', return_value=mock_client
            ),
            patch('sys.argv', ['mcp-registry', 'info', 'test-server']),
        ):
            result = await async_main()

        mock_client.get_server_by_name.assert_called_once_with('test-server')
        assert result == 0

    @pytest.mark.asyncio
    async def test_info_command_not_found(self) -> None:
        """Test info command when server not found."""
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get_server_by_name.return_value = None

        with (
            patch(
                'mcp_registry_client.commands.info.RegistryClient', return_value=mock_client
            ),
            patch('sys.argv', ['mcp-registry', 'info', 'nonexistent']),
        ):
            result = await async_main()

        assert result == 1

    @pytest.mark.asyncio
    async def test_info_command_json_output(self, sample_server, capsys) -> None:
        """Test info command with JSON output."""
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get_server_by_name.return_value = sample_server

        with (
            patch(
                'mcp_registry_client.commands.info.RegistryClient', return_value=mock_client
            ),
            patch('sys.argv', ['mcp-registry', '--json', 'info', 'test-server']),
        ):
            result = await async_main()

        assert result == 0

        captured = capsys.readouterr()
        output_data = json.loads(captured.out)
        assert output_data['name'] == 'test-server'
        assert output_data['repository']['url'] == 'https://github.com/test/repo'

    @pytest.mark.asyncio
    async def test_invalid_command(self) -> None:
        """Test handling of invalid command."""
        with patch('sys.argv', ['mcp-registry', 'invalid-command']):
            with pytest.raises(SystemExit) as exc_info:
                await async_main()

        # argparse raises SystemExit for invalid commands
        assert exc_info.value.code == 2

    def test_main_entry_point_success(self) -> None:
        """Test main entry point success."""
        with patch('mcp_registry_client.cli.asyncio.run', return_value=0) as mock_run:
            result = main()

        mock_run.assert_called_once()
        assert result == 0

    def test_main_entry_point_keyboard_interrupt(self) -> None:
        """Test main entry point KeyboardInterrupt handling."""
        with patch('mcp_registry_client.cli.asyncio.run', side_effect=KeyboardInterrupt):
            result = main()

        assert result == 130
