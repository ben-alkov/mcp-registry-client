# MCP Registry Client

A modern Python client for searching and retrieving MCP (Model Context Protocol)
servers from the official registry.

## Features

- 🔍 **Search Servers**: Find MCP servers by name with powerful filtering
- 📋 **Server Details**: Get comprehensive information about any server
- 🚀 **Async Support**: Built with modern async/await patterns
- 🛡️ **Type Safe**: Full type hints with Pydantic models
- 🎯 **CLI Interface**: Easy-to-use command-line interface
- 📦 **Modern Tooling**: Built with uv, hatch, and modern Python practices

## Quick Start

Install the package:

```bash
pip install mcp-registry-client
```

Search for servers:

```bash
mcp-registry search gmail
```

Get detailed server information:

```bash
mcp-registry info "ai.waystation/gmail"
```

## Python API

Use the client programmatically:

```python
import asyncio
from mcp_registry_client import RegistryClient

async def main():
    async with RegistryClient() as client:
        # Search for servers
        result = await client.search_servers(name="gmail")
        for server in result.servers:
            print(f"{server.name}: {server.description}")

        # Get specific server details
        server = await client.get_server_by_name("ai.waystation/gmail")
        if server:
            print(f"Version: {server.version}")
            print(f"Repository: {server.repository.url}")

asyncio.run(main())
```

## Requirements

- Python 3.12+
- Modern async HTTP client (httpx)
- Type-safe data validation (pydantic)

## Links

- [GitHub Repository](https://github.com/user/mcp-registry-client)
- [PyPI Package](https://pypi.org/project/mcp-registry-client)
- [MCP Registry](https://registry.modelcontextprotocol.io)
- [Model Context Protocol](https://modelcontextprotocol.io)
