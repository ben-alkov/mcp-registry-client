# MCP Registry Client

[![Python 3.12+][python-badge]][python-downloads]
[![License: GPLv3][license-badge]][license-link]
[![Tests][tests-badge]][tests-link]
[![Coverage][coverage-badge]][coverage-link]
[![Code Quality][quality-badge]][quality-link]
[![Ruff][ruff-badge]][ruff-link]
[![MyPy][mypy-badge]][mypy-link]

A Python client for searching and retrieving MCP servers from the
[Official MCP Registry][mcp-registry].

## Features

- 🔍 **Search MCP servers** by name with filtering
- 📋 **Get detailed server information** including packages, dependencies, and metadata
- 🖥️ **Command-line interface** for easy terminal usage
- 🐍 **Python API** for programmatic integration
- ⚡ **Async support** with modern Python patterns
- 🎯 **Type-safe** with comprehensive type hints
- 📚 **Well documented** with examples and API reference

## Installation

<!--
Install from PyPI (when published):

```bash
pip install mcp-registry-client
```
-->

Install from source:

```bash
git clone https://github.com/ben-alkov/mcp-registry-client.git
cd mcp-registry-client

# create virtual environment
# suggested
uv venv --seed --relocatable --link-mode copy --python-preference only-managed --no-cache --python 3.12 --prompt mcp-registry-client .venv

uv pip install -e . -r requirements.txt
```

Configuration is possible via "config.toml".

Edit "config.toml.example" (in the root of the repo) and rename to
"config.toml" if you need to use it.

You can use environment variables if you choose to.

## Quick Start

### Command Line Interface

Search for MCP servers:

```bash
# Search by name
mcp-registry search jira

# Get JSON output
mcp-registry --json search jira
```

Get detailed server information:

```bash
# Get server details
mcp-registry info "ai.waystation/jira"

# Get server info as JSON
mcp-registry --json info "ai.waystation/jira"
```

### Python API

```python
import asyncio
from mcp_registry_client import RegistryClient

async def main():
    async with RegistryClient() as client:
        # Search for servers
        result = await client.search_servers(name="jira")

        for server in result.servers:
            print(f"📧 {server.name}: {server.description}")

        # Get detailed server info
        server = await client.get_server_by_name("ai.waystation/jira")
        if server:
            print(f"\\n📋 {server.name}")
            print(f"   Version: {server.version}")
            print(f"   Repository: {server.repository.url}")

asyncio.run(main())
```

## API Reference

### RegistryClient

The main client class for interacting with the MCP registry:

```python
from mcp_registry_client import RegistryClient

# Initialize with default settings
client = RegistryClient()

# Custom configuration
client = RegistryClient(
    base_url="https://registry.modelcontextprotocol.io",
    timeout=30.0
)
```

#### Methods

- `search_servers(name: Optional[str] = None)` → `SearchResponse`
  - Search for servers with optional name filtering
- `get_server_by_name(name: str)` → `Optional[Server]`
  - Get server details by name (searches then fetches by ID)
- `get_server_by_id(server_id: str)` → `Server`
  - Get server details by registry ID

### Models

All response data is validated using Pydantic models:

- `Server` - Complete server information
- `SearchResponse` - List of servers from search
- `Package` - Package/dependency information
- `Repository` - Source repository details

## CLI Reference

```bash
mcp-registry --help

# Search command
mcp-registry  [--json] search NAME

# Info command
mcp-registry  [--json] info SERVER_NAME

# Global options
mcp-registry --verbose --json COMMAND
```

## Development

This is TL;DR, see [CONTRIBUTING](CONTRIBUTING.md)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and quality checks (`nox -s quality`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Setup

```bash
# Clone repository
git clone https://github.com/ben-alkov/mcp-registry-client.git
cd mcp-registry-client

# create venv
# suggested
uv venv --seed --relocatable --link-mode copy --python-preference only-managed --no-cache --python 3.12 --prompt mcp-registry-client .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install
# e.g. for everything
uv pip install -e ".[dev,docs]" -r requirements.txt -r requirements-dev.txt -r requirements-docs.txt
```

### Testing

```bash
# Run all tests
nox -s tests

# Run specific Python version
nox -s "tests-3.12"

# Run tests directly
pytest
```

### Code Quality

```bash
# Run all quality checks
nox -s quality

# Individual checks
nox -s format_source # Code formatting
nox -s lint          # Ruff linting
nox -s type_check    # MyPy type checking
nox -s security      # Bandit security analysis
```

### Documentation

```bash
# Build docs
nox -s docs

# Serve docs locally (don't run in CI)
nox -s docs_serve
```

## Configuration

See "config.toml.example" in the root of the repo. An alternative is to use
environment variables if you choose to.

### Custom Registry via API

```python
# Point to a different registry
client = RegistryClient(base_url="https://my-custom-registry.com")
```

## Error Handling

The client provides specific exception types:

```python
from mcp_registry_client import RegistryAPIError, RegistryClientError

try:
    async with RegistryClient() as client:
        result = await client.search_servers()
except RegistryAPIError as e:
    # API returned an error (4xx/5xx)
    print(f"API Error: {e} (Status: {e.status_code})")
except RegistryClientError as e:
    # Client-side error (parsing, validation, etc.)
    print(f"Client Error: {e}")
```

## Requirements

- Python 3.12+
- httpx >= 0.25.0
- pydantic >= 2.5.0

## License

This project is licensed under the GPL-3.0-or-later License - see LICENSE in the
root of the repo for details.

## Acknowledgments

- [Model Context Protocol][] for the specification
- [Official MCP Registry][mcp-registry] for the API
- Built with modern Python tools: [uv][], [ruff][], [nox][]

## Links

- 📖 [Documentation][]
- 🐛 [Issue Tracker][]
<!--
- 💬 [Discussions][]
- 📦 [PyPI Package][]
[Discussions]: https://github.com/ben-alkov/mcp-registry-client/discussions
[PyPI Package]: https://pypi.org/project/mcp-registry-client
-->

[Documentation]: https://ben-alkov.github.io/mcp-registry-client
[Issue Tracker]: https://github.com/ben-alkov/mcp-registry-client/issues
[mcp-registry]: https://registry.modelcontextprotocol.io
[Model Context Protocol]: https://modelcontextprotocol.io
[nox]: https://nox.thea.codes
[python-badge]: https://img.shields.io/badge/python-3.12+-blue.svg
[python-downloads]: https://www.python.org/downloads
[ruff]: https://github.com/astral-sh/ruff
[uv]: https://github.com/astral-sh/uv

<!-- Badge definitions -->
[coverage-badge]: https://img.shields.io/badge/coverage-90%25-brightgreen.svg
[coverage-link]: #testing
[license-badge]: https://img.shields.io/badge/License-GPLv3-yellow.svg
[license-link]: https://www.gnu.org/licenses/gpl-3.0.html#license-text
[mypy-badge]: https://img.shields.io/badge/type%20checked-mypy-blue.svg
[mypy-link]: https://mypy.readthedocs.io
[quality-badge]: https://img.shields.io/badge/code%20quality-A-brightgreen.svg
[quality-link]: #code-quality
[ruff-badge]: https://img.shields.io/badge/linted%20with-ruff-red.svg
[ruff-link]: https://docs.astral.sh/ruff/
[tests-badge]: https://img.shields.io/badge/tests-47%20passed-brightgreen.svg
[tests-link]: #testing
