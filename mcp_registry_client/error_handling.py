"""Error handling utilities for the MCP registry client."""

import logging

from .client import RegistryAPIError, RegistryClientError
from .constants import HTTP_INTERNAL_SERVER_ERROR, HTTP_NOT_FOUND
from .formatters import print_error

logger = logging.getLogger(__name__)


def handle_command_error(exc: Exception, context: str = '') -> int:
    """Handle command errors with consistent messaging and logging.

    Args:
        exc: The exception that occurred
        context: Additional context about the operation that failed

    Returns:
        Appropriate exit code for the error type

    """
    if isinstance(exc, RegistryAPIError):
        if hasattr(exc, 'status_code') and exc.status_code is not None:
            if exc.status_code == HTTP_NOT_FOUND:
                print_error(f'Error: Server not found{f" ({context})" if context else ""}')
            elif exc.status_code >= HTTP_INTERNAL_SERVER_ERROR:
                print_error('Error: Registry service unavailable. Please try again later.')
            else:
                print_error(f'Error: API request failed (HTTP {exc.status_code})')
        else:
            print_error(f'Error: API request failed{f" ({context})" if context else ""}')
        logger.debug('API error details: %s', exc)
        return 1
    if isinstance(exc, RegistryClientError):
        print_error(
            f'Error: Failed to process response{f" ({context})" if context else ""}'
        )
        logger.debug('Client error details: %s', exc)
        return 1
    print_error(f'Error: Unexpected error occurred{f" ({context})" if context else ""}')
    logger.exception('Unexpected error')
    return 1
