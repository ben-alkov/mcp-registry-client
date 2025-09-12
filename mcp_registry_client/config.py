"""Configuration management for the MCP registry client."""

import os
from dataclasses import dataclass

from .constants import (
    DEFAULT_BACKOFF_FACTOR,
    DEFAULT_BASE_URL,
    DEFAULT_CACHE_TTL,
    DEFAULT_CONNECT_TIMEOUT,
    DEFAULT_MAX_RETRIES,
    DEFAULT_POOL_TIMEOUT,
    DEFAULT_READ_TIMEOUT,
    DEFAULT_RETRY_DELAY,
    DEFAULT_TIMEOUT,
    DEFAULT_USER_AGENT,
    DEFAULT_WRITE_TIMEOUT,
)


@dataclass
class ClientConfig:
    """Configuration for the registry client."""

    # Connection settings
    base_url: str = DEFAULT_BASE_URL
    timeout: float = DEFAULT_TIMEOUT  # Overall timeout (backward compatibility)
    connect_timeout: float = DEFAULT_CONNECT_TIMEOUT
    read_timeout: float = DEFAULT_READ_TIMEOUT
    write_timeout: float = DEFAULT_WRITE_TIMEOUT
    pool_timeout: float = DEFAULT_POOL_TIMEOUT
    user_agent: str = DEFAULT_USER_AGENT

    # Retry settings
    max_retries: int = DEFAULT_MAX_RETRIES
    retry_delay: float = DEFAULT_RETRY_DELAY
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR

    # Cache settings
    cache_ttl: int = DEFAULT_CACHE_TTL
    enable_cache: bool = True

    @classmethod
    def from_env(cls) -> 'ClientConfig':
        """Create configuration from environment variables.

        Environment variables:
            MCP_REGISTRY_BASE_URL: Base URL for the registry API
            MCP_REGISTRY_TIMEOUT: Overall request timeout in seconds
            MCP_REGISTRY_CONNECT_TIMEOUT: Connection timeout in seconds
            MCP_REGISTRY_READ_TIMEOUT: Read timeout in seconds
            MCP_REGISTRY_WRITE_TIMEOUT: Write timeout in seconds
            MCP_REGISTRY_POOL_TIMEOUT: Connection pool timeout in seconds
            MCP_REGISTRY_USER_AGENT: User agent string
            MCP_REGISTRY_MAX_RETRIES: Maximum number of retries
            MCP_REGISTRY_RETRY_DELAY: Initial retry delay in seconds
            MCP_REGISTRY_BACKOFF_FACTOR: Exponential backoff factor
            MCP_REGISTRY_CACHE_TTL: Cache TTL in seconds
            MCP_REGISTRY_ENABLE_CACHE: Enable/disable caching (true/false)

        Returns:
            ClientConfig instance with values from environment variables

        """
        return cls(
            base_url=os.getenv('MCP_REGISTRY_BASE_URL', DEFAULT_BASE_URL),
            timeout=float(os.getenv('MCP_REGISTRY_TIMEOUT', str(DEFAULT_TIMEOUT))),
            connect_timeout=float(
                os.getenv('MCP_REGISTRY_CONNECT_TIMEOUT', str(DEFAULT_CONNECT_TIMEOUT))
            ),
            read_timeout=float(
                os.getenv('MCP_REGISTRY_READ_TIMEOUT', str(DEFAULT_READ_TIMEOUT))
            ),
            write_timeout=float(
                os.getenv('MCP_REGISTRY_WRITE_TIMEOUT', str(DEFAULT_WRITE_TIMEOUT))
            ),
            pool_timeout=float(
                os.getenv('MCP_REGISTRY_POOL_TIMEOUT', str(DEFAULT_POOL_TIMEOUT))
            ),
            user_agent=os.getenv('MCP_REGISTRY_USER_AGENT', DEFAULT_USER_AGENT),
            max_retries=int(
                os.getenv('MCP_REGISTRY_MAX_RETRIES', str(DEFAULT_MAX_RETRIES))
            ),
            retry_delay=float(
                os.getenv('MCP_REGISTRY_RETRY_DELAY', str(DEFAULT_RETRY_DELAY))
            ),
            backoff_factor=float(
                os.getenv('MCP_REGISTRY_BACKOFF_FACTOR', str(DEFAULT_BACKOFF_FACTOR))
            ),
            cache_ttl=int(os.getenv('MCP_REGISTRY_CACHE_TTL', str(DEFAULT_CACHE_TTL))),
            enable_cache=os.getenv('MCP_REGISTRY_ENABLE_CACHE', 'true').lower() == 'true',
        )


@dataclass
class CLIConfig:
    """Configuration for the CLI interface."""

    # Output settings
    default_output_format: str = 'table'  # 'table' or 'json'
    table_max_description_width: int = 60
    json_indent: int = 2

    # Logging settings
    default_log_level: str = 'INFO'
    verbose_log_level: str = 'DEBUG'

    @classmethod
    def from_env(cls) -> 'CLIConfig':
        """Create CLI configuration from environment variables.

        Environment variables:
            MCP_CLI_OUTPUT_FORMAT: Default output format (table/json)
            MCP_CLI_TABLE_MAX_DESC_WIDTH: Maximum description width in table format
            MCP_CLI_JSON_INDENT: JSON indentation level
            MCP_CLI_LOG_LEVEL: Default log level
            MCP_CLI_VERBOSE_LOG_LEVEL: Verbose mode log level

        Returns:
            CLIConfig instance with values from environment variables

        """
        return cls(
            default_output_format=os.getenv('MCP_CLI_OUTPUT_FORMAT', 'table'),
            table_max_description_width=int(
                os.getenv('MCP_CLI_TABLE_MAX_DESC_WIDTH', '60')
            ),
            json_indent=int(os.getenv('MCP_CLI_JSON_INDENT', '2')),
            default_log_level=os.getenv('MCP_CLI_LOG_LEVEL', 'INFO'),
            verbose_log_level=os.getenv('MCP_CLI_VERBOSE_LOG_LEVEL', 'DEBUG'),
        )


def get_client_config(
    base_url: str | None = None,
    timeout: float | None = None,
    **kwargs: str | float | bool,
) -> ClientConfig:
    """Get client configuration with optional overrides.

    Args:
        base_url: Override base URL
        timeout: Override timeout
        **kwargs: Additional configuration overrides

    Returns:
        ClientConfig instance

    """
    config = ClientConfig.from_env()

    if base_url is not None:
        config.base_url = base_url
    if timeout is not None:
        config.timeout = timeout

    for key, value in kwargs.items():
        if hasattr(config, key) and value is not None:
            setattr(config, key, value)

    return config


def get_cli_config(**kwargs: str | int) -> CLIConfig:
    """Get CLI configuration with optional overrides.

    Args:
        **kwargs: Configuration overrides

    Returns:
        CLIConfig instance

    """
    config = CLIConfig.from_env()

    for key, value in kwargs.items():
        if hasattr(config, key) and value is not None:
            setattr(config, key, value)

    return config
