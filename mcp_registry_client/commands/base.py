"""Base command class for CLI command pattern implementation."""

import argparse
from abc import ABC, abstractmethod
from typing import Any

from mcp_registry_client.client import RegistryClientError
from mcp_registry_client.error_handling import handle_command_error
from mcp_registry_client.formatters import print_error


class BaseCommand(ABC):
    """Abstract base class for CLI commands.

    Provides a standard interface for command validation, execution,
    and output formatting.
    """

    def __init__(self, args: argparse.Namespace) -> None:
        """Initialize command with parsed arguments.

        Args:
            args: Parsed command line arguments

        """
        self.args = args

    @abstractmethod
    def validate_args(self) -> None:
        """Validate command arguments.

        Raises:
            ValueError: If arguments are invalid

        """

    @abstractmethod
    async def execute(self) -> Any:  # noqa: ANN401
        """Execute the command logic.

        Returns:
            Command execution result

        Raises:
            Exception: Various exceptions based on command implementation

        """

    @abstractmethod
    def format_output(self, result: Any) -> None:  # noqa: ANN401
        """Format and display command output.

        Args:
            result: Result from execute() method

        """

    async def run(self) -> int:
        """Run the complete command workflow.

        Returns:
            Exit code (0 for success, non-zero for error)

        """
        try:
            self.validate_args()
            result: Any = await self.execute()
            self.format_output(result)
        except KeyboardInterrupt:
            raise
        except (ValueError, RegistryClientError, OSError, RuntimeError) as e:
            return self._handle_error(e)
        else:
            return 0

    def _handle_error(self, exc: Exception) -> int:
        """Handle command errors with consistent messaging.

        Args:
            exc: The exception that occurred

        Returns:
            Appropriate exit code for the error type

        """
        # Handle ValueError specially (user input validation errors)
        if isinstance(exc, ValueError):
            print_error(f'Error: {exc}')
            return 1

        context = f'{self.__class__.__name__.lower().replace("command", "")} operation'
        return handle_command_error(exc, context)
