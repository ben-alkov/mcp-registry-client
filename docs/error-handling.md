# Error Handling

This document describes the error handling patterns used in the MCP Registry
Client and how to handle different types of errors in your applications.

## Exception Hierarchy

The client uses a structured exception hierarchy that helps you handle different
types of errors appropriately:

```text
Exception
├── httpx.HTTPError (from httpx library)
│   ├── httpx.RequestError (network/transport issues)
│   │   ├── httpx.ConnectError (connection failures)
│   │   ├── httpx.TimeoutException (request timeouts)
│   │   └── httpx.NetworkError (other network issues)
│   └── httpx.HTTPStatusError (4xx/5xx responses)
├── ValidationError (from pydantic library)
└── RegistryClientError (custom exceptions)
    └── RegistryAPIError (API-specific errors)
```

## Custom Exceptions

### RegistryClientError

Base exception for all client-specific errors.

```python
from mcp_registry_client import RegistryClientError

try:
    # client operations
    pass
except RegistryClientError as e:
    print(f"Client error: {e}")
```

### RegistryAPIError

Raised when the registry API returns an error response. Includes the HTTP
status code when available.

```python
from mcp_registry_client import RegistryAPIError

try:
    server = await client.get_server_by_name("nonexistent")
except RegistryAPIError as e:
    if e.status_code == 404:
        print("Server not found")
    elif e.status_code >= 500:
        print("Registry service unavailable")
    else:
        print(f"API error: {e}")
```

## Common Error Scenarios

### Network Issues

Network connectivity problems are handled by httpx exceptions:

```python
import httpx
from mcp_registry_client import RegistryClient

async def handle_network_errors():
    try:
        async with RegistryClient() as client:
            result = await client.search_servers()
    except httpx.ConnectError:
        print("Failed to connect to registry")
    except httpx.TimeoutException:
        print("Request timed out")
    except httpx.NetworkError as e:
        print(f"Network error: {e}")
```

### API Response Errors

Handle different HTTP status codes appropriately:

```python
import httpx
from mcp_registry_client import RegistryAPIError

async def handle_api_errors():
    try:
        async with RegistryClient() as client:
            server = await client.get_server_by_name("server-name")
    except RegistryAPIError as e:
        if e.status_code == 404:
            print("Server not found")
        elif e.status_code == 429:
            print("Rate limited - please try again later")
        elif e.status_code >= 500:
            print("Registry service temporarily unavailable")
    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e.response.status_code}")
```

### Data Validation Errors

Pydantic validation errors occur when the API returns unexpected data:

```python
from pydantic import ValidationError

async def handle_validation_errors():
    try:
        async with RegistryClient() as client:
            result = await client.search_servers()
    except ValidationError as e:
        print(f"Invalid response format: {e}")
        # Log the error for debugging
        logger.error("Validation error", exc_info=True)
```

## Best Practices

### Comprehensive Error Handling

Always handle the most specific exceptions first:

```python
import httpx
from pydantic import ValidationError
from mcp_registry_client import RegistryAPIError, RegistryClientError

async def robust_client_usage():
    try:
        async with RegistryClient() as client:
            result = await client.search_servers(name="example")
            return result.servers
    except RegistryAPIError as e:
        if e.status_code == 404:
            return []  # No servers found
        elif e.status_code >= 500:
            raise  # Re-raise server errors
        else:
            logger.warning(f"API error: {e}")
            return []
    except httpx.RequestError as e:
        logger.error(f"Network error: {e}")
        raise  # Re-raise network errors
    except ValidationError as e:
        logger.error(f"Data validation error: {e}")
        raise  # Re-raise validation errors
    except RegistryClientError as e:
        logger.error(f"Client error: {e}")
        raise
```

### Retry Logic

Implement retry logic for transient errors:

```python
import asyncio
import httpx
from mcp_registry_client import RegistryAPIError

async def retry_on_transient_errors(max_retries=3):
    for attempt in range(max_retries):
        try:
            async with RegistryClient() as client:
                return await client.search_servers()
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            if attempt == max_retries - 1:
                raise  # Re-raise on final attempt
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
        except RegistryAPIError as e:
            if e.status_code and e.status_code >= 500:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
            else:
                raise  # Don't retry client errors (4xx)
```

### Logging

Use appropriate logging levels for different error types:

```python
import logging
from mcp_registry_client import RegistryAPIError, RegistryClientError

logger = logging.getLogger(__name__)

async def log_errors_appropriately():
    try:
        async with RegistryClient() as client:
            result = await client.search_servers()
    except RegistryAPIError as e:
        if e.status_code == 404:
            logger.info("Server not found")
        elif e.status_code >= 500:
            logger.error(f"Registry service error: {e}")
        else:
            logger.warning(f"API error: {e}")
    except RegistryClientError as e:
        logger.error(f"Client error: {e}")
    except Exception as e:
        logger.exception("Unexpected error")
```

### Context Managers

Always use the client as a context manager to ensure proper cleanup:

```python
# Good
async with RegistryClient() as client:
    result = await client.search_servers()

# Avoid
client = RegistryClient()
try:
    result = await client.search_servers()
finally:
    await client.close()
```

## CLI Error Handling

The CLI interface handles errors gracefully and provides user-friendly messages:

- **404 errors**: "Server not found"
- **5xx errors**: "Registry service unavailable. Please try again later."
- **Network errors**: Specific error messages based on the failure type
- **Validation errors**: "Failed to process response"

All CLI errors are logged with appropriate detail levels for debugging.