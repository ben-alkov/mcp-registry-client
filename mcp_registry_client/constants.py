"""Constants for the MCP registry client."""

import tomllib
from pathlib import Path

# HTTP status codes
HTTP_OK = 200
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_METHOD_NOT_ALLOWED = 405
HTTP_TOO_MANY_REQUESTS = 429
HTTP_INTERNAL_SERVER_ERROR = 500
HTTP_BAD_GATEWAY = 502
HTTP_SERVICE_UNAVAILABLE = 503
HTTP_GATEWAY_TIMEOUT = 504


def _load_config() -> dict:
    """Load configuration from config.toml file."""
    config_path = Path(__file__).parent.parent / 'config.toml'
    if config_path.exists():
        with config_path.open('rb') as f:
            return tomllib.load(f)
    return {}


# Load configuration
_config = _load_config()
_client_config = _config.get('client', {})

# Default configuration values with fallbacks
DEFAULT_BASE_URL = _client_config.get(
    'base_url', 'https://registry.modelcontextprotocol.io'
)
DEFAULT_TIMEOUT = _client_config.get('timeout', 30.0)
DEFAULT_CONNECT_TIMEOUT = _client_config.get('connect_timeout', 10.0)
DEFAULT_READ_TIMEOUT = _client_config.get('read_timeout', 30.0)
DEFAULT_WRITE_TIMEOUT = _client_config.get('write_timeout', 10.0)
DEFAULT_POOL_TIMEOUT = _client_config.get('pool_timeout', 5.0)
DEFAULT_USER_AGENT = _client_config.get('user_agent', 'mcp-registry-client/0.1.0')

# Request retry configuration
DEFAULT_MAX_RETRIES = _client_config.get('max_retries', 3)
DEFAULT_RETRY_DELAY = _client_config.get('retry_delay', 1.0)
DEFAULT_BACKOFF_FACTOR = _client_config.get('backoff_factor', 2.0)

# Response caching configuration
DEFAULT_CACHE_TTL = _client_config.get('cache_ttl', 300)  # 5 minutes in seconds
