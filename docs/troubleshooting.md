# Troubleshooting Guide

This guide helps you diagnose and resolve common issues when using the MCP
Registry Client.

## Installation Issues

### Python Version Compatibility

**Problem**: ImportError or syntax errors when importing the client.

**Solution**: Ensure you're using Python 3.12 or later:

```bash
python --version
# Should show Python 3.12.x or higher
```

If you need to upgrade Python, consider using [pyenv][] or [uv][]:

```bash
# Using uv
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.12

# Using pyenv  
pyenv install 3.12.0
pyenv global 3.12.0
```

### Missing Dependencies

**Problem**: ModuleNotFoundError for httpx or pydantic.

**Solution**: Install with all dependencies:

```bash
pip install mcp-registry-client
# or
uv pip install mcp-registry-client
```

For development dependencies:

```bash
pip install "mcp-registry-client[dev]"
```

## Network Issues

### Connection Refused

**Problem**: `ConnectError` when trying to reach the registry.

**Symptoms**:

```text
httpx.ConnectError: [Errno 111] Connection refused
```

**Solutions**:

1. **Check internet connection**:

   ```bash
   curl -I https://registry.modelcontextprotocol.io
   ```

2. **Verify DNS resolution**:

   ```bash
   nslookup registry.modelcontextprotocol.io
   ```

3. **Check firewall/proxy settings**:

   ```python
   # Use custom proxy
   from mcp_registry_client import RegistryClient
   
   async with RegistryClient() as client:
       client._client.proxies = {
           "https://": "http://proxy.company.com:8080"
       }
   ```

### SSL/TLS Issues

**Problem**: SSL verification errors.

**Symptoms**:

```text
ssl.SSLCertVerificationError: certificate verify failed
```

**Solutions**:

1. **Update certificates**:

   ```bash
   # On macOS
   /Applications/Python\ 3.x/Install\ Certificates.command
   
   # On Ubuntu/Debian
   sudo apt-get update && sudo apt-get install ca-certificates
   ```

2. **Check system time**: Ensure your system clock is correct.

3. **Corporate network**: Configure certificates for corporate networks:

   ```python
   import httpx
   from mcp_registry_client import RegistryClient
   
   # Custom client with cert bundle
   async with RegistryClient() as client:
       client._client.verify = "/path/to/corporate-ca-bundle.pem"
   ```

### Timeout Issues

**Problem**: Requests timing out.

**Symptoms**:

```text
httpx.TimeoutException: timed out
```

**Solutions**:

1. **Increase timeout**:

   ```python
   from mcp_registry_client import RegistryClient
   
   # Increase timeout to 60 seconds
   async with RegistryClient(timeout=60.0) as client:
       result = await client.search_servers()
   ```

2. **Check network stability**:

   ```bash
   ping -c 10 registry.modelcontextprotocol.io
   ```

3. **Use retry logic** (see [Error Handling](error-handling.md#retry-logic)).

## API Issues

### Rate Limiting

**Problem**: HTTP 429 (Too Many Requests) errors.

**Symptoms**:

```text
RegistryAPIError: Too Many Requests (429)
```

**Solutions**:

1. **Implement backoff**:

   ```python
   import asyncio
   from mcp_registry_client import RegistryAPIError
   
   async def search_with_backoff(client, **kwargs):
       for delay in [1, 2, 4, 8]:
           try:
               return await client.search_servers(**kwargs)
           except RegistryAPIError as e:
               if e.status_code == 429:
                   await asyncio.sleep(delay)
               else:
                   raise
       raise  # Final attempt failed
   ```

2. **Reduce request frequency**: Add delays between requests.

3. **Cache results**: Store responses to avoid repeated requests.

### Server Not Found

**Problem**: Getting 404 errors for servers you expect to exist.

**Solutions**:

1. **Check server name format**:

   ```bash
   # Correct format includes namespace
   mcp-registry info "ai.waystation/gmail"
   
   # Not just the server name
   mcp-registry info gmail
   ```

2. **Search first to find exact name**:

   ```bash
   mcp-registry search --name gmail
   ```

3. **Check if server was recently added**: The registry may not be
   immediately updated.

### Invalid Response Format

**Problem**: ValidationError when processing responses.

**Symptoms**:

```text
pydantic.ValidationError: 1 validation error for SearchResponse
```

**Solutions**:

1. **Check registry status**: The API might be returning unexpected data.

2. **Update client**: Ensure you're using the latest version:

   ```bash
   pip install --upgrade mcp-registry-client
   ```

3. **Report the issue**: If the error persists, it might be an API change.

## CLI Issues

### Command Not Found

**Problem**: `mcp-registry: command not found`

**Solutions**:

1. **Check installation**:

   ```bash
   pip show mcp-registry-client
   pip install --force-reinstall mcp-registry-client
   ```

2. **Check PATH**: Ensure pip's bin directory is in your PATH:

   ```bash
   python -m pip show -f mcp-registry-client | grep console_scripts
   ```

3. **Use module syntax**:

   ```bash
   python -m mcp_registry_client.cli search
   ```

### JSON Output Issues

**Problem**: Malformed JSON output or encoding errors.

**Solutions**:

1. **Check terminal encoding**:

   ```bash
   echo $LANG
   # Should include UTF-8
   ```

2. **Redirect to file**:

   ```bash
   mcp-registry search --json > results.json
   ```

3. **Use Python API** for programmatic access instead of parsing CLI output.

## Performance Issues

### Slow Responses

**Problem**: Requests taking too long to complete.

**Solutions**:

1. **Use connection pooling**:

   ```python
   import httpx
   from mcp_registry_client import RegistryClient
   
   # Reuse client instance
   client = RegistryClient()
   async with client:
       # Multiple requests reuse connections
       result1 = await client.search_servers(name="server1")
       result2 = await client.search_servers(name="server2")
   ```

2. **Implement caching**:

   ```python
   from functools import lru_cache
   import asyncio
   
   @lru_cache(maxsize=128)
   def _cache_key(name):
       return name
   
   _cache = {}
   
   async def cached_search(client, name=None):
       key = _cache_key(name)
       if key not in _cache:
           _cache[key] = await client.search_servers(name=name)
       return _cache[key]
   ```

3. **Use specific searches**: Search with name filters to reduce response size.

### Memory Usage

**Problem**: High memory usage with large result sets.

**Solutions**:

1. **Process results in chunks**:

   ```python
   async def process_servers_chunked(client):
       result = await client.search_servers()
       for server in result.servers:
           # Process one server at a time
           await process_single_server(server)
           # Explicit cleanup if needed
           del server
   ```

2. **Use generators** when possible.

3. **Limit result sets** with specific search criteria.

## Development Issues

### Testing

**Problem**: Tests failing due to network dependencies.

**Solutions**:

1. **Use httpx mock**:

   ```python
   import pytest
   import httpx
   from mcp_registry_client import RegistryClient
   
   @pytest.mark.asyncio
   async def test_search_with_mock(httpx_mock):
       httpx_mock.add_response(
           method="GET",
           url="https://registry.modelcontextprotocol.io/v0/servers",
           json={"servers": [], "total": 0}
       )
       
       async with RegistryClient() as client:
           result = await client.search_servers()
           assert result.total == 0
   ```

2. **Use pytest fixtures** for common test data.

3. **Test error conditions** separately from happy path tests.

### Type Checking

**Problem**: mypy errors with the client.

**Solutions**:

1. **Update type hints**:

   ```python
   from typing import Optional
   from mcp_registry_client import RegistryClient, Server
   
   async def get_server_info(name: str) -> Optional[Server]:
       async with RegistryClient() as client:
           return await client.get_server_by_name(name)
   ```

2. **Use proper imports**:

   ```python
   # Good
   from mcp_registry_client import RegistryClient
   
   # Avoid
   import mcp_registry_client
   client = mcp_registry_client.RegistryClient()
   ```

## Getting Help

If you're still experiencing issues:

1. **Check the logs**: Enable debug logging:

   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   
   # Your client code here
   ```

2. **Review error handling**: See the [Error Handling Guide](error-handling.md).

3. **Check for updates**: Ensure you're using the latest version.

4. **Report bugs**: Create an issue with:
   - Python version
   - Client version
   - Full error traceback
   - Minimal reproduction code

## Common Environment Variables

Set these environment variables to customize behavior:

```bash
# HTTP proxy
export HTTPS_PROXY=http://proxy.company.com:8080

# Certificate bundle
export REQUESTS_CA_BUNDLE=/path/to/ca-bundle.pem

# Debug logging
export PYTHONPATH=/path/to/debug/logging/config
```

[pyenv]: https://github.com/pyenv/pyenv
[uv]: https://docs.astral.sh/uv/