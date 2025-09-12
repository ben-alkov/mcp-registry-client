<!-- markdownlint-disable-file MD029 -->

# Development Troubleshooting

This guide helps developers troubleshoot common issues encountered during
development, testing, and contributing to the MCP Registry Client.

## Test-Related Issues

### Unit Test Failures

#### Import Errors in Tests

**Problem**: `ImportError` or `ModuleNotFoundError` when running tests.

**Solution**:

```bash
# Ensure package is installed in development mode
uv pip install -e ".[dev]"

# Verify your virtual environment is activated
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

#### Async Test Issues

**Problem**: Tests fail with `RuntimeWarning: coroutine was never awaited` or
similar async errors.

**Solution**:

```python
# Ensure async tests are properly marked
@pytest.mark.asyncio
async def test_my_async_function(self) -> None:
    """Test async functionality."""
    result = await my_async_function()
    assert result is not None

# For mocking async functions, use AsyncMock
from unittest.mock import AsyncMock

mock_client = AsyncMock()
mock_client.search_servers.return_value = expected_result
```

#### Coverage Issues

**Problem**: Coverage reports show unexpected missing lines or lower than
expected coverage.

**Common Causes & Solutions**:

1. **Missing `__init__.py` files**: Ensure all test directories have
   `__init__.py` files.
2. **Import-time side effects**: Code executed during import may not be covered.
3. **Exception handling**: Some error paths might not be tested.

```bash
# Generate detailed coverage report
pytest --cov=mcp_registry_client --cov-report=html --cov-report=term-missing

# Check which lines are missing coverage
open htmlcov/index.html
```

### Integration Test Issues

#### Network Connectivity Problems

**Problem**: Integration tests fail due to network issues or API unavailability.

**Solution**:

```bash
# Run only unit tests during development
pytest tests/ -m "not integration"

# Check your network connection
curl -I https://registry.modelcontextprotocol.io

# Use pytest marks to skip problematic tests
pytest tests/ -m "integration and not slow"
```

#### Rate Limiting

**Problem**: Tests fail due to API rate limiting.

**Solution**: Integration tests include built-in rate limiting, but if you
encounter issues:

```python
# Increase delays in test configuration
rate_limiter = RateLimiter(calls_per_second=0.2)  # Slower rate

# Or run fewer concurrent tests
pytest tests/integration/ -x  # Stop on first failure
```

### Performance Test Issues

#### Benchmark Failures

**Problem**: Performance tests fail because operations take longer than expected.

**Solution**:

```bash
# Run benchmarks individually to isolate issues
pytest tests/performance/test_cache_performance.py::TestCachePerformance::test_cache_set_performance -v

# Check system load during benchmarks
# Performance thresholds may need adjustment on slower systems
```

**Adjusting Performance Thresholds**:

```python
# In performance tests, adjust timing assertions for your environment
assert operation_time < 2.0, f'Operation took too long: {operation_time:.3f}s'
# Consider increasing threshold on slower CI systems
```

## Development Environment Issues

### Virtual Environment Problems

**Problem**: Package installation or import issues.

**Solution**:

```bash
# Recreate virtual environment
rm -rf .venv
uv venv
source .venv/bin/activate
uv pip install -e ".[dev,docs]"

# Verify installation
python -c "import mcp_registry_client; print('Success')"
```

### Dependency Conflicts

**Problem**: Dependency version conflicts or missing dependencies.

**Solution**:

```bash
# Check for dependency conflicts
uv pip check

# Update dependencies
uv pip install --upgrade pip
uv pip install -e ".[dev,docs]" --force-reinstall

# If using pip instead of uv
pip install --upgrade pip setuptools wheel
```

### IDE Configuration Issues

#### Type Checking Problems

**Problem**: IDE shows type errors that don't appear in mypy runs.

**Solution**:

1. Ensure your IDE is using the correct Python interpreter from your virtual environment
2. Configure IDE to use the same mypy settings as the project:

```json
// VS Code settings.json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.linting.mypyEnabled": true,
    "python.linting.mypyArgs": ["--config-file", "pyproject.toml"]
}
```

#### Import Resolution

**Problem**: IDE cannot resolve imports from the local package.

**Solution**:

```bash
# Ensure package is installed in development mode
uv pip install -e .

# Or add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## Code Quality Issues

### Linting Failures

#### Ruff Errors

**Problem**: Ruff reports formatting or linting errors.

**Solution**:

```bash
# Auto-fix most issues
nox -s format_source

# Check specific errors
ruff check . --show-source

# Fix imports
ruff check . --select I --fix
```

#### MyPy Type Errors

**Problem**: Type checking failures.

**Common Issues & Solutions**:

1. **Missing type annotations**:

```python
# Bad
def process_data(data):
    return data.upper()

# Good
def process_data(data: str) -> str:
    return data.upper()
```

2. **Async function annotations**:

```python
# Bad
async def fetch_data():
    return await client.get()

# Good
async def fetch_data() -> dict[str, Any]:
    return await client.get()
```

3. **Generic types**:

```python
# Bad
from typing import List, Dict

def process_items(items: List) -> Dict:
    pass

# Good
def process_items(items: list[str]) -> dict[str, int]:
    pass
```

### Security Analysis Issues

**Problem**: Bandit reports security issues.

**Solution**:

```bash
# Run security analysis
nox -s security

# Review findings and either fix or exclude if false positive
# Add exclusions to pyproject.toml if needed
```

## Testing Best Practices for Troubleshooting

### Debugging Test Failures

1. **Use verbose output**:

```bash
pytest tests/test_example.py::test_function -v -s
```

2. **Add debugging prints**:

```python
def test_my_function():
    result = my_function()
    print(f"Debug: result = {result}")  # Temporary debug line
    assert result is not None
```

3. **Use pytest debugging**:

```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger on first failure
pytest --pdb -x
```

### Isolating Test Issues

1. **Run tests individually**:

```bash
pytest tests/test_client.py::TestRegistryClient::test_search_servers -v
```

2. **Run related tests only**:

```bash
pytest tests/ -k "test_cache"
```

3. **Skip problematic tests temporarily**:

```python
@pytest.mark.skip(reason="Under investigation")
def test_problematic_function():
    pass
```

## Performance Debugging

### Profiling Test Performance

```bash
# Profile test execution
pytest tests/ --profile

# Use cProfile for detailed analysis
python -m cProfile -o profile_output.prof -m pytest tests/
```

### Memory Debugging

```python
# Add memory usage tracking to tests
import tracemalloc

def test_memory_usage():
    tracemalloc.start()

    # Your test code here

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
    print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
```

## Getting Help

If you encounter issues not covered in this guide:

1. **Check existing issues**: Search the project's GitHub issues for similar problems
2. **Run diagnostics**:

   ```bash
   # System information
   python --version
   uv --version

   # Package information
   uv pip list

   # Test environment
   pytest --collect-only
   ```

3. **Create a minimal reproduction**: Isolate the problem to the smallest
   possible test case
4. **Report the issue**: Include system information, error messages, and
   reproduction steps

## Common Error Messages

### `ModuleNotFoundError: No module named 'mcp_registry_client'`

**Solution**: Install package in development mode: `uv pip install -e .`

### `ImportError: cannot import name 'X' from 'mcp_registry_client.Y'`

**Solution**: Check import paths and ensure the module structure is correct

### `RuntimeError: There is no current event loop in thread`

**Solution**: Mark async tests with `@pytest.mark.asyncio`

### `AssertionError: assert 1 == 0`

**Solution**: Check test logic and expected values; use descriptive assertion messages

### `TypeError: object Mock can't be used in 'await' expression`

**Solution**: Use `AsyncMock` instead of `Mock` for async functions

This troubleshooting guide should help you resolve common development issues
quickly and get back to productive coding and testing.
