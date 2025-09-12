"""Retry logic for network requests."""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import TypeVar

import httpx

from .config import ClientConfig
from .constants import HTTP_INTERNAL_SERVER_ERROR, HTTP_TOO_MANY_REQUESTS

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryStrategy:
    """Retry strategy for network requests."""

    def __init__(self, config: ClientConfig) -> None:
        """Initialize retry strategy.

        Args:
            config: Client configuration with retry settings

        """
        self.max_retries = config.max_retries
        self.retry_delay = config.retry_delay
        self.backoff_factor = config.backoff_factor

    def should_retry(self, attempt: int, exception: Exception) -> bool:
        """Determine if a request should be retried.

        Args:
            attempt: Current attempt number (0-based)
            exception: The exception that occurred

        Returns:
            True if the request should be retried

        """
        if attempt >= self.max_retries:
            return False

        # Retry on network errors and specific HTTP status codes
        if isinstance(exception, httpx.RequestError):
            return True

        if isinstance(exception, httpx.HTTPStatusError):
            # Retry on server errors (5xx) and rate limiting (429)
            status_code = exception.response.status_code
            return (
                status_code >= HTTP_INTERNAL_SERVER_ERROR
                or status_code == HTTP_TOO_MANY_REQUESTS
            )

        return False

    def get_delay(self, attempt: int) -> float:
        """Calculate delay before next retry.

        Args:
            attempt: Current attempt number (0-based)

        Returns:
            Delay in seconds

        """
        return self.retry_delay * (self.backoff_factor**attempt)


async def with_retry[T](
    func: Callable[[], Awaitable[T]],
    strategy: RetryStrategy,
    operation_name: str = 'operation',
) -> T:
    """Execute an async function with retry logic.

    Args:
        func: Async function to execute
        strategy: Retry strategy to use
        operation_name: Name of the operation for logging

    Returns:
        Result of the function call

    Raises:
        Exception: The last exception if all retries are exhausted

    """
    last_exception = None

    for attempt in range(strategy.max_retries + 1):
        try:
            return await func()
        except (
            httpx.RequestError,
            httpx.HTTPStatusError,
            OSError,
            TimeoutError,
        ) as e:
            last_exception = e

            if not strategy.should_retry(attempt, e):
                logger.debug(
                    '%s failed on attempt %d/%d, not retrying: %s',
                    operation_name,
                    attempt + 1,
                    strategy.max_retries + 1,
                    e,
                )
                break

            if attempt < strategy.max_retries:
                delay = strategy.get_delay(attempt)
                logger.debug(
                    '%s failed on attempt %d/%d, retrying in %.2fs: %s',
                    operation_name,
                    attempt + 1,
                    strategy.max_retries + 1,
                    delay,
                    e,
                )
                await asyncio.sleep(delay)
            else:
                logger.debug(
                    '%s failed on final attempt %d/%d: %s',
                    operation_name,
                    attempt + 1,
                    strategy.max_retries + 1,
                    e,
                )

    # Re-raise the last exception
    if last_exception is not None:
        raise last_exception

    # This should never happen, but satisfy type checker
    msg = f'{operation_name} failed with no exception recorded'
    raise RuntimeError(msg)
