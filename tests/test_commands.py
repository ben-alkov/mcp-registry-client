"""Tests for command pattern implementation."""

import argparse
import json
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from mcp_registry_client.client import RegistryAPIError
from mcp_registry_client.commands import InfoCommand, SearchCommand
from mcp_registry_client.models import (
    OfficialMeta,
    Repository,
    Server,
    ServerMeta,
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


class TestSearchCommand:
    """Tests for SearchCommand."""

    def test_validate_args_success(self) -> None:
        """Test successful argument validation."""
        args = argparse.Namespace(name='test-query', json=False)
        command = SearchCommand(args)

        # Should not raise any exception
        command.validate_args()

    def test_validate_args_empty_name(self) -> None:
        """Test validation failure with empty name."""
        args = argparse.Namespace(name='', json=False)
        command = SearchCommand(args)

        with pytest.raises(ValueError, match='Search term cannot be empty'):
            command.validate_args()

    def test_validate_args_whitespace_name(self) -> None:
        """Test validation failure with whitespace-only name."""
        args = argparse.Namespace(name='   ', json=False)
        command = SearchCommand(args)

        with pytest.raises(ValueError, match='Search term cannot be empty'):
            command.validate_args()

    @pytest.mark.asyncio
    async def test_execute_success(self, sample_server) -> None:
        """Test successful command execution."""
        args = argparse.Namespace(name='test-query', json=False)
        command = SearchCommand(args)

        mock_result = Mock()
        mock_result.servers = [sample_server]

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.search_servers.return_value = mock_result

        with patch(
            'mcp_registry_client.commands.search.RegistryClient', return_value=mock_client
        ):
            result = await command.execute()

        mock_client.search_servers.assert_called_once_with(name='test-query')
        assert result.servers == [sample_server]

    def test_format_output_table(self, sample_server, capsys) -> None:
        """Test table output formatting."""
        args = argparse.Namespace(name='test-query', json=False)
        command = SearchCommand(args)

        mock_result = Mock()
        mock_result.servers = [sample_server]

        command.format_output(mock_result)

        captured = capsys.readouterr()
        assert 'test-server' in captured.out
        assert '1.0.0' in captured.out

    def test_format_output_json(self, sample_server, capsys) -> None:
        """Test JSON output formatting."""
        args = argparse.Namespace(name='test-query', json=True)
        command = SearchCommand(args)

        mock_result = Mock()
        mock_result.servers = [sample_server]

        command.format_output(mock_result)

        captured = capsys.readouterr()
        output_data = json.loads(captured.out)
        assert len(output_data) == 1
        assert output_data[0]['name'] == 'test-server'

    @pytest.mark.asyncio
    async def test_run_success(self, sample_server) -> None:
        """Test complete command run workflow."""
        args = argparse.Namespace(name='test-query', json=False)
        command = SearchCommand(args)

        mock_result = Mock()
        mock_result.servers = [sample_server]

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.search_servers.return_value = mock_result

        with patch(
            'mcp_registry_client.commands.search.RegistryClient', return_value=mock_client
        ):
            result = await command.run()

        assert result == 0

    @pytest.mark.asyncio
    async def test_run_validation_error(self) -> None:
        """Test command run with validation error."""
        args = argparse.Namespace(name='', json=False)
        command = SearchCommand(args)

        result = await command.run()
        assert result == 1

    @pytest.mark.asyncio
    async def test_run_api_error(self) -> None:
        """Test command run with API error."""
        args = argparse.Namespace(name='test-query', json=False)
        command = SearchCommand(args)

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.search_servers.side_effect = RegistryAPIError('API failed')

        with patch(
            'mcp_registry_client.commands.search.RegistryClient', return_value=mock_client
        ):
            result = await command.run()

        assert result == 1


class TestInfoCommand:
    """Tests for InfoCommand."""

    def test_validate_args_success(self) -> None:
        """Test successful argument validation."""
        args = argparse.Namespace(server_name='test-server', json=False)
        command = InfoCommand(args)

        # Should not raise any exception
        command.validate_args()

    def test_validate_args_empty_server_name(self) -> None:
        """Test validation failure with empty server name."""
        args = argparse.Namespace(server_name='', json=False)
        command = InfoCommand(args)

        with pytest.raises(ValueError, match='Server name cannot be empty'):
            command.validate_args()

    @pytest.mark.asyncio
    async def test_execute_success(self, sample_server) -> None:
        """Test successful command execution."""
        args = argparse.Namespace(server_name='test-server', json=False)
        command = InfoCommand(args)

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get_server_by_name.return_value = sample_server

        with patch(
            'mcp_registry_client.commands.info.RegistryClient', return_value=mock_client
        ):
            result = await command.execute()

        mock_client.get_server_by_name.assert_called_once_with('test-server')
        assert result == sample_server

    @pytest.mark.asyncio
    async def test_execute_server_not_found(self) -> None:
        """Test execution when server is not found."""
        args = argparse.Namespace(server_name='nonexistent', json=False)
        command = InfoCommand(args)

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get_server_by_name.return_value = None

        with patch(
            'mcp_registry_client.commands.info.RegistryClient', return_value=mock_client
        ):
            with pytest.raises(ValueError, match='Server "nonexistent" not found'):
                await command.execute()

    def test_format_output_human_readable(self, sample_server, capsys) -> None:
        """Test human-readable output formatting."""
        args = argparse.Namespace(server_name='test-server', json=False)
        command = InfoCommand(args)

        command.format_output(sample_server)

        captured = capsys.readouterr()
        assert 'test-server' in captured.out

    def test_format_output_json(self, sample_server, capsys) -> None:
        """Test JSON output formatting."""
        args = argparse.Namespace(server_name='test-server', json=True)
        command = InfoCommand(args)

        command.format_output(sample_server)

        captured = capsys.readouterr()
        output_data = json.loads(captured.out)
        assert output_data['name'] == 'test-server'

    @pytest.mark.asyncio
    async def test_run_success(self, sample_server) -> None:
        """Test complete command run workflow."""
        args = argparse.Namespace(server_name='test-server', json=False)
        command = InfoCommand(args)

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get_server_by_name.return_value = sample_server

        with patch(
            'mcp_registry_client.commands.info.RegistryClient', return_value=mock_client
        ):
            result = await command.run()

        assert result == 0

    @pytest.mark.asyncio
    async def test_run_server_not_found(self) -> None:
        """Test command run when server is not found."""
        args = argparse.Namespace(server_name='nonexistent', json=False)
        command = InfoCommand(args)

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get_server_by_name.return_value = None

        with patch(
            'mcp_registry_client.commands.info.RegistryClient', return_value=mock_client
        ):
            result = await command.run()

        assert result == 1
