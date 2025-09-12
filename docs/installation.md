# Installation

## Requirements

- Python 3.12 or higher
- pip or uv package manager

## Install from PyPI

The easiest way to install MCP Registry Client is from PyPI:

```bash
pip install mcp-registry-client
```

## Install with uv

If you're using [uv](https://github.com/astral-sh/uv) (recommended):

```bash
uv pip install mcp-registry-client
```

## Install from Source

For development or to get the latest features:

```bash
git clone https://github.com/user/mcp-registry-client.git
cd mcp-registry-client
uv pip install -e .
```

## Development Installation

For contributing to the project:

```bash
git clone https://github.com/user/mcp-registry-client.git
cd mcp-registry-client

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode with all dependencies
uv pip install -e ".[dev,docs]"
```

## Verify Installation

Check that the installation was successful:

```bash
mcp-registry --help
```

You should see the help output for the CLI tool.

## Optional Dependencies

The package has optional dependency groups:

- `dev`: Development tools (pytest, mypy, ruff, etc.)
- `docs`: Documentation building (mkdocs-material, etc.)

Install with optional dependencies:

```bash
pip install "mcp-registry-client[dev,docs]"
```