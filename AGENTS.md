# AGENTS.md

*AFTER READING* this file, always say 'I have remembered the project AGENTS.md memory file'

This file provides guidance to AI agents when working with code in this repository.

!!! ALWAYS activate the virtual environment with `source .venv/bin/activate`

!!! ALWAYS use `unset GITHUB_TOKEN;` when calling the `gh` command

## Recent Changes (Last 3)

- **2025-09-16**: Added Claude Code MCP Registry Integration feature (001-add-feature-s)
  - MCP server-based integration for registry search and installation
  - Support for local/project/user configuration scopes
  - Natural language interfaces for server discovery and management

## Architecture

### Core Components

- **Client Layer** (`client.py`): Async HTTP client using httpx for registry API
  communication
- **Models** (`models.py`): Pydantic models for API responses (Server,
  SearchResponse, Package, Repository)
- **CLI Interface** (`cli.py`): Command-line interface with search and info
  commands
- **Commands** (`commands/`): Modular command implementations (search, info)
  with base command pattern
- **Error Handling** (`error_handling.py`): Centralized error handling utilities
- **Configuration** (`config.py`): Environment-based configuration management
- **Caching** (`cache.py`): Response caching with TTL for performance
  optimization
- **Retry Logic** (`retry.py`): Configurable retry strategies for API resilience

### Claude Code Integration (Feature 001-add-feature-s)

- **Claude Integration** (`claude_integration.py`): MCP server for Claude Code
  integration
- **Claude Tools** (`claude_tools.py`): Tool implementations for search,
  details, installation
- **Claude Models** (extended `models.py`): Claude-specific request/response
  models

### Key Patterns

- **Async/await**: All API operations are async using httpx
- **Pydantic validation**: Strong typing and validation for all API responses
- **Error handling**: Custom exception hierarchy (RegistryClientError,
  RegistryAPIError)
- **Configuration**: Environment variables with sensible defaults; end-user
  config via TOML config file
- **Testing structure**: Separate integration, benchmark, and unit test suites
- **MCP Integration**: Server-based tool integration following Claude Code
  conventions

## Commands

### Development Setup

```bash
# Install in development mode with all dependencies
uv pip install -e ".[dev,docs]"
```

### Using Nox Sessions

```bash
nox -s tests          # Run tests for all Python versions
nox -s "tests-3.12"   # Run tests for specific Python version
nox -s lint           # Linting and format checks
nox -s type_check     # MyPy type checking
nox -s format_source  # Format code
nox -s security       # Security analysis
nox -s docs           # Build documentation
```

### Manual CI/testing

#### Testing

```bash
# Run all tests (excluding benchmark tests)
pytest -m "not benchmark"

# Run specific test types
pytest -m "not integration and not benchmark"  # Unit tests only
pytest -m integration                          # Integration tests only
pytest -m benchmark                           # Benchmark tests only

# Run tests directly with pytest
pytest                                         # All tests with coverage
pytest tests/test_client.py                   # Specific test file
pytest tests/test_cli.py::TestCLI -v         # Specific test class
```

#### Code Quality

```bash
# Format code
ruff format .
ruff check --fix .

# Type checking
mypy mcp_registry_client/

# Security analysis
bandit -r mcp_registry_client

# Run all quality checks via nox
nox -s quality
```

## Claude Code Integration Features

### MCP Registry Tools

- **search_servers**: Natural language search for MCP servers with pagination
- **get_server_info**: Detailed server information and installation requirements
- **install_server**: Guided installation with scope selection (local/project/user)

### Usage Examples

```bash
# Search for servers
"Find an MCP server for JIRA in the registry"

# Get detailed information
"Get more info on atlassian/mcp-jira"

# Install with scope selection
"Install atlassian/mcp-jira"
# Prompts for local/project/user scope choice
```

### Configuration Scopes

- **Local**: Private to user in current project (default)
- **Project**: Shared team configuration in .mcp.json
- **User**: Available across all user projects

### Error Handling

- Graceful degradation with structured error responses
- User-friendly error messages with actionable guidance
- Network error handling with retry logic
- Installation validation and rollback support

## Important Implementation Notes

- Always use IDE diagnostics to validate code after implementation
- Always verify that there is ONE single newline at the end of any file which
  you edit
- Follow constitutional requirements for library-first architecture
- Use Test-Driven Development with contract tests before implementation
- Maintain backward compatibility and semantic versioning

## Entry Points

- CLI: `mcp-registry` command (defined in pyproject.toml scripts)
- Python API: Import `RegistryClient` from `mcp_registry_client`
- Claude Code: MCP server integration via `claude_integration.py`

## Testing Configuration

- Uses pytest with asyncio mode enabled
- Test markers: `integration`, `benchmark`, `slow`
- Coverage reporting to both terminal and HTML
- Benchmark tests are excluded from default runs
- Contract tests for Claude Code integration tools
