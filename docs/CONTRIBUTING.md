# Contributing

Thank you for your interest in contributing to MCP Registry Client! This guide
will help you get started.

## Development Setup

### Prerequisites

- Python 3.12+
- [uv][]
- Git

### Setting up the Development Environment

1. Fork and clone the repository

   ```bash
   git clone https://github.com/yourusername/mcp-registry-client.git
   cd mcp-registry-client
   ```

2. Create a virtual environment

   ```bash
   # suggested
   uv venv --seed --relocatable --link-mode copy --python-preference only-managed --no-cache --python 3.12 --prompt mcp-registry-client .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install development dependencies

    Regular dev only

   ```bash
   uv pip install -e ".[dev]" -r requirements.txt -r requirements-dev.txt
   ```

    Docs dev only

   ```bash
   uv pip install -e ".[docs]" -r requirements.txt -r requirements-docs.txt
   ```

   Everything

   ```bash
   uv pip install -e ".[dev,docs]" -r requirements.txt -r requirements-dev.txt -r requirements-docs.txt
   ```

4. Hack

## Development Workflow

We use [Nox][] for standardized development tasks.

### Code Quality

Run all quality checks

```bash
nox -s quality
```

Or run individual checks

```bash
# Linting and formatting
nox -s lint

# Type checking
nox -s type_check

# Security analysis
nox -s security

# Format code
nox -s format_source
```

### Testing

Run tests

```bash
nox -s tests
```

Run tests with coverage

```bash
nox -s tests -- --cov-report=html
```

### Documentation

Build documentation

```bash
nox -s docs
```

Serve documentation locally

```bash
nox -s docs_serve
```

## Code Style

We use the following tools to maintain code quality

- **Ruff**: For linting, formatting, and import sorting
- **mypy**: For type checking
- **bandit**: For security analysis
- **pytest**: For testing

### Code Formatting

Code is automatically formatted with Ruff. Run the formatter

```bash
nox -s format_source
```

### Type Hints

All code must include comprehensive type hints. We use

- Python 3.12+ type syntax
- Pydantic for data validation
- Strict mypy configuration

### Docstrings

Use Google-style docstrings

```python
def example_function(param: str, optional: int = 0) -> str
    """Brief description of the function.

    Longer description if needed. Explain the purpose, behavior,
    and any important details.

    Args
        param: Description of the parameter.
        optional: Description of optional parameter.

    Returns
        Description of the return value.

    Raises
        ValueError: When and why this exception is raised.
    """
    return f"Result: {param} + {optional}"
```

## Testing Guidelines

### Test Structure

Tests are organized in the `tests/` directory with three main categories

```text
tests/
├── test_*.py                      # Unit tests
├── integration/                   # Integration tests with real APIs
│   ├── test_real_api.py
│   └── test_cli_integration.py
└── performance/                   # Performance benchmarks
    ├── test_cache_performance.py
    ├── test_retry_performance.py
    └── test_client_performance.py
```

### Testing Strategy

This project employs comprehensive testing patterns including

- **Edge Case Testing**: Boundary conditions, error states, and concurrency scenarios
- **Integration Testing**: Real API interactions with rate limiting
- **Performance Testing**: Benchmarks for critical performance paths

For detailed testing patterns and guidelines, see [Testing Patterns](testing-patterns.md).

### Running Different Test Categories

```bash
# Unit tests only (default for development)
pytest tests/ -m "not integration and not benchmark"

# Integration tests (requires network access)
pytest tests/ -m "integration"

# Performance benchmarks
pytest tests/ -m "benchmark"

# All tests
pytest tests/
```

### Writing Tests

- Use descriptive test names that explain what is being tested
- Include comprehensive docstrings for complex test scenarios
- Test both success and error cases, especially edge conditions
- Use appropriate fixtures and mocking strategies
- Follow the patterns documented in [Testing Patterns](testing-patterns.md)

Example edge case test

```python
@pytest.mark.asyncio
async def test_concurrent_cache_access(self) -> None
    """Test concurrent access to the same cache key."""
    cache = ResponseCache(config)

    async def set_value(key: str, value: str) -> None
        await cache.set(key, value)

    # Run multiple sets concurrently to test race conditions
    await asyncio.gather(
        set_value('test-key', 'value1'),
        set_value('test-key', 'value2'),
        set_value('test-key', 'value3'),
    )

    assert len(cache._cache) == 1
    result = await cache.get('test-key')
    assert result in ['value1', 'value2', 'value3']
```

### Test Coverage Requirements

- **Overall Coverage**: >90%
- **Core Modules**: 100% coverage for `client.py`, `cache.py`, `models.py`
- **CLI Module**: >95% coverage

Check coverage with

```bash
nox -s tests -- --cov-report=html
open htmlcov/index.html
```

### Performance Testing

Performance tests use pytest-benchmark and are marked with
`@pytest.mark.benchmark`.

These tests

- Validate response times for critical operations
- Test behavior under concurrent load
- Monitor memory usage patterns
- Ensure retry mechanisms perform efficiently

Run performance tests separately

```bash
pytest tests/ -m "benchmark" --benchmark-only
```

## Submitting Changes

### Pull Request Process

1. Create a feature branch

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit

   ```bash
   git add .
   git commit -m "Add: brief description of changes"
   ```

3. Run quality checks

   ```bash
   nox -s quality
   ```

4. Push and create a pull request

   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Messages

Use [Conventional Commits][] format

We use the following set of "types". If you have one which isn't listed, feel
free to use it. If we hate it, we'll let you know. OTOH, we might even adopt it :D.

- agents: agent-related changes (AGENTS.md, "agent-notes" dir)
- build: build system changes
- chore: tech-debt
- ci: CI/CD changes
- docs: documentation changes
- feat: new features
- fix: bug fixes
- perf: performance-related changes
- refactor: refactoring changes - note that this is separate from chore
- repo: .gitignore; git options; folder/file reorg; etc.
- revert: reverting previous commits
- test: test changes (net-new, fixes, refactor, ...)

TL;DR

```text
type(scope?, scope?, ...): subject
body?
footer?
```

Examples

```text
feat(server): support for server filtering by category
fix(api): handle API timeout errors gracefully
docs(api): add API usage examples
```

### Pull Request Requirements

- All tests must pass
- Code coverage should not decrease
- All quality checks must pass
- Include tests for new functionality
- Update documentation if needed
- Include a clear description of changes

## Release Process

Releases are handled by maintainers

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create a release tag
<!--
4. GitHub Actions handles PyPI publication
-->
## Getting Help

- Open an issue for bugs or feature requests
- Start a discussion for questions or ideas
- Check existing issues before creating new ones

## Code of Conduct

This project follows the [Contributor Covenant][].
Be respectful and inclusive in all interactions.

[Contributor Covenant]: https://www.contributor-covenant.org
[Conventional Commits]: https://www.conventionalcommits.org/en/v1.0.0/#specification
[Nox]: https://nox.thea.codes
[uv]: https://github.com/astral-sh/uv
