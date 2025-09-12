"""Integration tests for CLI with real API interactions."""

import json
import subprocess
import time
from pathlib import Path

import pytest


def run_cli_command(args: list[str], timeout: int = 30) -> subprocess.CompletedProcess:
    """Run CLI command and return result.

    Args:
        args: Command line arguments
        timeout: Timeout in seconds

    Returns:
        CompletedProcess result

    """
    # Add rate limiting between CLI calls
    time.sleep(1)

    # Use the proper mcp-registry command
    cmd = ['mcp-registry', *args]

    return subprocess.run(  # noqa: S603
        cmd,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=Path(__file__).parent.parent.parent,
    )


@pytest.mark.integration
class TestCLIIntegration:
    """Integration tests for CLI with real API."""

    def test_cli_search_real_api(self) -> None:
        """Test CLI search command with real API."""
        result = run_cli_command(['search', 'git'])

        assert result.returncode == 0
        assert 'NAME' in result.stdout
        assert 'DESCRIPTION' in result.stdout
        assert 'VERSION' in result.stdout

        # Should have at least some results
        lines = result.stdout.strip().split('\n')
        assert len(lines) > 2  # Header + separator + at least one result

    def test_cli_search_json_output_real_api(self) -> None:
        """Test CLI search with JSON output using real API."""
        result = run_cli_command(['--json', 'search', 'git'])

        assert result.returncode == 0

        # Should be valid JSON
        data = json.loads(result.stdout)
        assert isinstance(data, list)

        # Should have some results
        assert len(data) > 0

        # Check structure of first result
        first_result = data[0]
        assert 'name' in first_result
        assert 'description' in first_result
        assert 'repository' in first_result
        assert 'version' in first_result

    def test_cli_search_no_results_real_api(self) -> None:
        """Test CLI search with no results using real API."""
        # Note: The MCP registry API appears to return all results for any search term
        # This test verifies the command runs successfully even with unlikely search terms
        result = run_cli_command(['search', 'nonexistent-mcp-server-xyz-123'])

        assert result.returncode == 0
        # The API currently returns results for any search term, so we just check it
        # succeeded
        assert 'NAME' in result.stdout or 'No servers found.' in result.stdout

    def test_cli_info_real_api(self) -> None:
        """Test CLI info command with real API."""
        # First get a server name from search
        search_result = run_cli_command(['--json', 'search', 'git'])
        assert search_result.returncode == 0

        search_data = json.loads(search_result.stdout)
        if search_data:
            server_name = search_data[0]['name']

            # Now get info for that server
            result = run_cli_command(['info', server_name])

            assert result.returncode == 0
            assert f'Name: {server_name}' in result.stdout
            assert 'Description:' in result.stdout
            assert 'Repository:' in result.stdout

    def test_cli_info_json_output_real_api(self) -> None:
        """Test CLI info with JSON output using real API."""
        # First get a server name from search
        search_result = run_cli_command(['--json', 'search', 'git'])
        assert search_result.returncode == 0

        search_data = json.loads(search_result.stdout)
        if search_data:
            server_name = search_data[0]['name']

            # Now get info for that server in JSON format
            result = run_cli_command(['--json', 'info', server_name])

            assert result.returncode == 0

            # Should be valid JSON
            data = json.loads(result.stdout)
            assert isinstance(data, dict)
            assert data['name'] == server_name
            assert 'repository' in data
            assert 'metadata' in data

    def test_cli_info_nonexistent_server_real_api(self) -> None:
        """Test CLI info for nonexistent server using real API."""
        result = run_cli_command(['info', 'nonexistent-server-xyz-123'])

        assert result.returncode == 1
        assert 'Error: Server "nonexistent-server-xyz-123" not found' in result.stderr

    def test_cli_verbose_logging_real_api(self) -> None:
        """Test CLI with verbose logging using real API."""
        result = run_cli_command(['--verbose', 'search', 'git'])

        assert result.returncode == 0
        # Verbose mode should still work and produce output
        assert 'NAME' in result.stdout

    def test_cli_help_commands(self) -> None:
        """Test CLI help commands."""
        # Test main help
        result = run_cli_command(['--help'])
        assert result.returncode == 0
        assert 'mcp-registry' in result.stdout
        assert 'Search and retrieve MCP servers' in result.stdout

        # Test search help
        result = run_cli_command(['search', '--help'])
        assert result.returncode == 0
        assert 'Search term to find servers' in result.stdout

        # Test info help
        result = run_cli_command(['info', '--help'])
        assert result.returncode == 0
        assert 'Name of the server to get information about' in result.stdout

    def test_cli_invalid_command(self) -> None:
        """Test CLI with invalid command."""
        result = run_cli_command(['invalid-command'])

        assert result.returncode == 2
        assert 'invalid choice' in result.stderr

    def test_cli_missing_required_arguments(self) -> None:
        """Test CLI with missing required arguments."""
        # Search command requires name argument
        result = run_cli_command(['search'])
        assert result.returncode == 2
        assert 'required' in result.stderr.lower() or 'arguments' in result.stderr.lower()

        # Info command requires server_name argument
        result = run_cli_command(['info'])
        assert result.returncode == 2
        assert 'required' in result.stderr.lower() or 'arguments' in result.stderr.lower()


@pytest.mark.integration
@pytest.mark.slow
class TestCLIStressIntegration:
    """Stress tests for CLI integration."""

    def test_cli_multiple_rapid_requests(self) -> None:
        """Test CLI handling of multiple rapid requests."""
        # This tests if the CLI can handle being called multiple times quickly
        # without issues like connection pooling problems

        results = []
        for _ in range(3):
            result = run_cli_command(['--json', 'search', 'git'])
            results.append(result)
            # Small delay to avoid overwhelming the API
            time.sleep(0.5)

        # All requests should succeed
        for result in results:
            assert result.returncode == 0
            data = json.loads(result.stdout)
            assert isinstance(data, list)

    def test_cli_long_running_search(self) -> None:
        """Test CLI with potentially long-running search."""
        # Search for a very common term that might return many results
        result = run_cli_command(['search', 'server'], timeout=60)

        assert result.returncode == 0
        # Should complete within timeout and return results
        assert 'NAME' in result.stdout or 'No servers found.' in result.stdout
