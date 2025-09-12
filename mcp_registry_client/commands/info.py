"""Info command implementation."""

import argparse

from mcp_registry_client.client import RegistryClient
from mcp_registry_client.config import get_cli_config
from mcp_registry_client.formatters import (
    format_server_detailed,
    print_json,
    print_server_info_human_readable,
)
from mcp_registry_client.models import Server
from mcp_registry_client.validation import validate_server_name

from .base import BaseCommand


class InfoCommand(BaseCommand):
    """Command to get detailed information about a specific server."""

    def __init__(self, args: argparse.Namespace) -> None:
        """Initialize info command.

        Args:
            args: Parsed command line arguments containing 'server_name' and 'json'

        """
        super().__init__(args)

    def validate_args(self) -> None:
        """Validate info command arguments.

        Raises:
            ValueError: If server name is invalid

        """
        validate_server_name(self.args.server_name)

    async def execute(self) -> Server:
        """Execute the info command.

        Returns:
            Server information from the registry client

        Raises:
            RegistryAPIError: If API request fails
            RegistryClientError: If client processing fails
            httpx.RequestError: If HTTP request fails
            ValidationError: If response validation fails
            ValueError: If server is not found

        """
        async with RegistryClient() as client:
            server = await client.get_server_by_name(self.args.server_name)

            if server is None:
                msg = f'Server "{self.args.server_name}" not found'
                raise ValueError(msg)

            return server

    def format_output(self, result: Server) -> None:
        """Format and display server information.

        Args:
            result: Server object with detailed information

        """
        cli_config = get_cli_config()

        if self.args.json:
            data = format_server_detailed(result)
            print_json(data, indent=cli_config.json_indent)
        else:
            print_server_info_human_readable(result)
