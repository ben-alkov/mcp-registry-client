# Quick Start

This guide will help you get started with MCP Registry Client quickly.

## Command Line Interface

### Search for Servers

Search for servers by name:

```bash
mcp-registry search jira
```

Get JSON output for programmatic use:

```bash
mcp-registry search --json jira
```

### Get Server Information

Get detailed information about a specific server:

```bash
mcp-registry info "ai.waystation/jira"
```

Get server info in JSON format:

```bash
mcp-registry info --json "ai.waystation/jira"
```

## Python API

### Basic Usage

```python
import asyncio
from mcp_registry_client import RegistryClient

async def main():
    async with RegistryClient() as client:
        # Search all servers
        result = await client.search_servers()
        print(f"Found {len(result.servers)} servers")

        # Search with name filter
        gmail_servers = await client.search_servers(name="gmail")
        for server in gmail_servers.servers:
            print(f"- {server.name}: {server.description}")

asyncio.run(main())
```

### Get Server Details

```python
import asyncio
from mcp_registry_client import RegistryClient

async def main():
    async with RegistryClient() as client:
        # Get server by name
        server = await client.get_server_by_name("ai.waystation/gmail")

        if server:
            print(f"Name: {server.name}")
            print(f"Description: {server.description}")
            print(f"Version: {server.version}")
            print(f"Repository: {server.repository.url}")

            # Check for remote endpoints
            if server.remotes:
                print("Remote endpoints:")
                for remote in server.remotes:
                    print(f"  - {remote.type}: {remote.url}")

            # Check for packages
            if server.packages:
                print("Packages:")
                for package in server.packages:
                    print(f"  - {package.registry_type}: {package.identifier}")
        else:
            print("Server not found")

asyncio.run(main())
```

### Error Handling

```python
import asyncio
from mcp_registry_client import RegistryClient, RegistryAPIError, RegistryClientError

async def main():
    try:
        async with RegistryClient() as client:
            result = await client.search_servers(name="example")
            print(f"Found {len(result.servers)} servers")

    except RegistryAPIError as e:
        print(f"API Error: {e}")
        if e.status_code:
            print(f"Status Code: {e.status_code}")

    except RegistryClientError as e:
        print(f"Client Error: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")

asyncio.run(main())
```

### Custom Configuration

```python
import asyncio
from mcp_registry_client import RegistryClient

async def main():
    # Custom registry URL and timeout
    async with RegistryClient(
        base_url="https://custom.registry.com",
        timeout=60.0
    ) as client:
        result = await client.search_servers()
        print(f"Found {len(result.servers)} servers")

asyncio.run(main())
```

## Next Steps

- Read the [CLI Reference](cli.md) for detailed command options
- Check the [API Reference](api/mcp_registry_client/client.md) for complete Python API documentation
- Learn about [contributing](CONTRIBUTING.md) to the project
