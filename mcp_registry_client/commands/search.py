"""Search command implementation."""

import argparse

from mcp_registry_client.client import RegistryClient
from mcp_registry_client.config import get_cli_config
from mcp_registry_client.formatters import format_server_summary, print_json, print_table
from mcp_registry_client.models import SearchResponse
from mcp_registry_client.validation import validate_search_term

from .base import BaseCommand


class SearchCommand(BaseCommand):
    """Command to search for MCP servers in the registry."""

    def __init__(self, args: argparse.Namespace) -> None:
        """Initialize search command.

        Args:
            args: Parsed command line arguments containing 'name' and 'json'

        """
        super().__init__(args)

    def validate_args(self) -> None:
        """Validate search command arguments.

        Raises:
            ValueError: If search term is invalid

        """
        validate_search_term(self.args.name)

    async def execute(self) -> SearchResponse:
        """Execute the search command.

        Returns:
            Search result from the registry client

        Raises:
            RegistryAPIError: If API request fails
            RegistryClientError: If client processing fails
            httpx.RequestError: If HTTP request fails
            ValidationError: If response validation fails

        """
        async with RegistryClient() as client:
            return await client.search_servers(name=self.args.name)

    def format_output(self, result: SearchResponse) -> None:
        """Format and display search results.

        Args:
            result: Search result containing servers list

        """
        cli_config = get_cli_config()

        if self.args.json:
            data = [format_server_summary(server) for server in result.servers]
            print_json(data, indent=cli_config.json_indent)
        else:
            print_table(result.servers, cli_config.table_max_description_width)
