# CLAUDE.md

This file provides guidance to AI agents when working with code in this repository.

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

## Architecture

### Core Components

- **Client Layer** (`client.py`): Async HTTP client using httpx for registry API
  communication
- **Models** (`models.py`): Pydantic models for API responses (Server,
  SearchResponse, Package, Repository)
- **CLI Interface** (`cli.py`): Command-line interface with search and info commands
- **Commands** (`commands/`): Modular command implementations (search, info)
  with base command pattern
- **Error Handling** (`error_handling.py`): Centralized error handling utilities
- **Configuration** (`config.py`): Environment-based configuration management
- **Caching** (`cache.py`): Response caching with TTL for performance optimization
- **Retry Logic** (`retry.py`): Configurable retry strategies for API resilience

### Key Patterns

- **Async/await**: All API operations are async using httpx
- **Pydantic validation**: Strong typing and validation for all API responses
- **Error handling**: Custom exception hierarchy (RegistryClientError, RegistryAPIError)
- **Configuration**: Environment variables with sensible defaults; end-user
  config via TOML config file (example in "config.toml.example")
- **Testing structure**: Separate integration, benchmark, and unit test suites

### Entry Points

- CLI: `mcp-registry` command (defined in pyproject.toml scripts)
- Python API: Import `RegistryClient` from `mcp_registry_client`

### Testing Configuration

- Uses pytest with asyncio mode enabled
- Test markers: `integration`, `benchmark`, `slow`
- Coverage reporting to both terminal and HTML
- Benchmark tests are excluded from default runs
