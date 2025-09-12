"""Command-line interface for the MCP registry client."""

import argparse
import asyncio
import logging

from .commands import BaseCommand, InfoCommand, SearchCommand

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:  # noqa: FBT001, FBT002
    """Set up logging configuration."""
    # Set root logger to WARNING to avoid noise from third-party libraries
    root_level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=root_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

    # Set our application logger to INFO level for relevant app logs
    app_level = logging.DEBUG if verbose else logging.INFO
    logging.getLogger('mcp_registry_client').setLevel(app_level)

    # Specifically silence httpx unless in verbose mode
    if not verbose:
        logging.getLogger('httpx').setLevel(logging.WARNING)


# Command registry mapping command names to command classes
COMMAND_REGISTRY: dict[str, type[BaseCommand]] = {
    'search': SearchCommand,
    'info': InfoCommand,
}


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog='mcp-registry',
        description='Search and retrieve MCP servers from the official registry',
    )

    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging',
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format',
    )

    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands',
        required=True,
    )

    # Search command
    search_parser = subparsers.add_parser(
        'search',
        help='Search for MCP servers',
    )
    search_parser.add_argument(
        'name',
        help='Search term to find servers (required)',
    )

    # Info command
    info_parser = subparsers.add_parser(
        'info',
        help='Get detailed information about a specific server',
    )
    info_parser.add_argument(
        'server_name',
        help='Name of the server to get information about',
    )

    return parser


async def async_main() -> int:
    """Async main function."""
    parser = create_parser()
    args = parser.parse_args()

    setup_logging(verbose=args.verbose)

    # Get command class from registry
    command_class = COMMAND_REGISTRY.get(args.command)
    if command_class is None:
        parser.print_help()
        return 1

    # Create and run command
    command = command_class(args)
    return await command.run()


def main() -> int:
    """Run main entry point."""
    try:
        return asyncio.run(async_main())
    except KeyboardInterrupt:
        return 130
