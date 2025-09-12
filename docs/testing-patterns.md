# Testing Patterns and Guidelines

This document outlines the testing patterns, methodologies, and best practices used in the MCP Registry Client project. It serves as a guide for contributors and maintainers to ensure consistent, high-quality testing across the codebase.

## Overview

The project employs a comprehensive testing strategy with three main categories:

- **Unit Tests**: Fast, isolated tests for individual components
- **Integration Tests**: End-to-end tests with real API interactions
- **Performance Tests**: Benchmarks and load testing for performance validation

## Test Structure

```text
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures and configuration
├── test_*.py                      # Unit tests
├── integration/                   # Integration tests
│   ├── __init__.py
│   ├── conftest.py               # Integration-specific configuration
│   ├── test_real_api.py          # Real API interaction tests
│   └── test_cli_integration.py   # CLI integration tests
└── performance/                   # Performance benchmarks
    ├── __init__.py
    ├── test_cache_performance.py
    ├── test_retry_performance.py
    └── test_client_performance.py
```

## Unit Testing Patterns

### Edge Case Testing Strategy

The project emphasizes comprehensive edge case testing to ensure production resilience. Key patterns include:

#### 1. Boundary Condition Testing

```python
@pytest.mark.asyncio
async def test_zero_ttl(self) -> None:
    """Test cache behavior with zero TTL."""
    config.cache_ttl = 0
    cache = ResponseCache(config)

    with patch('time.time', return_value=1000.0):
        await cache.set('test-key', 'test-value')

    # Entry should be immediately expired
    with patch('time.time', return_value=1000.1):
        result = await cache.get('test-key')

    assert result is None
```

**Pattern**: Test boundary values (zero, negative, maximum) for all numeric parameters.

#### 2. Error State Testing

```python
@pytest.mark.asyncio
async def test_http_error_without_json_body(self) -> None:
    """Test HTTP error handling when response body is not JSON."""
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = 'Internal Server Error'
    mock_response.json.side_effect = ValueError('Not JSON')

    http_error = httpx.HTTPStatusError('Internal Server Error',
                                      request=Mock(), response=mock_response)

    with pytest.raises(RegistryAPIError) as exc_info:
        await client.search_servers('test')

    assert exc_info.value.status_code == 500
    assert 'HTTP 500: Internal Server Error' in str(exc_info.value)
```

**Pattern**: Test all error conditions, including malformed responses and network failures.

#### 3. Concurrency Testing

```python
@pytest.mark.asyncio
async def test_concurrent_access_same_key(self) -> None:
    """Test concurrent access to the same cache key."""
    cache = ResponseCache(config)

    async def set_value(key: str, value: str) -> None:
        await cache.set(key, value)

    # Run multiple sets concurrently
    await asyncio.gather(
        set_value('test-key', 'value1'),
        set_value('test-key', 'value2'),
        set_value('test-key', 'value3'),
    )

    assert len(cache._cache) == 1
    result = await cache.get('test-key')
    assert result in ['value1', 'value2', 'value3']
```

**Pattern**: Test concurrent operations to identify race conditions and data corruption issues.

### Mock Usage Guidelines

#### 1. Async Mocking

```python
mock_client = AsyncMock()
mock_client.__aenter__.return_value = mock_client
mock_client.__aexit__.return_value = None
mock_client.search_servers.return_value = mock_result
```

**Best Practice**: Always properly configure async context managers when mocking async clients.

#### 2. Side Effect Testing

```python
mock_response.json.side_effect = ValueError('Not JSON')
```

**Best Practice**: Use `side_effect` to test error conditions and dynamic behaviors.

#### 3. Call Verification

```python
mock_client.search_servers.assert_called_once_with(name='test')
```

**Best Practice**: Verify not just that functions were called, but with the correct arguments.

## Integration Testing Patterns

### Rate Limiting

Integration tests include built-in rate limiting to avoid overwhelming external APIs:

```python
class RateLimiter:
    """Simple rate limiter to avoid overwhelming the API."""
    
    def __init__(self, calls_per_second: float = 1.0) -> None:
        self._calls_per_second = calls_per_second
        self._last_call_time = 0.0
    
    async def wait(self) -> None:
        """Wait before allowing the next call."""
        current_time = time.time()
        time_since_last_call = current_time - self._last_call_time
        min_interval = 1.0 / self._calls_per_second
        
        if time_since_last_call < min_interval:
            await asyncio.sleep(min_interval - time_since_last_call)
        
        self._last_call_time = time.time()
```

### Real API Testing Strategy

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_search_servers_real_api(self) -> None:
    """Test searching servers with real API."""
    async with rate_limited_client() as client:
        result = await client.search_servers()
        
        # Validate structure without assuming specific content
        assert result is not None
        assert hasattr(result, 'servers')
        assert isinstance(result.servers, list)
        
        if result.servers:  # Only test if servers exist
            first_server = result.servers[0]
            assert hasattr(first_server, 'name')
            assert hasattr(first_server, 'repository')
```

**Pattern**: Test structure and behavior rather than specific content, as external APIs may change.

## Performance Testing Patterns

### Benchmark Structure

```python
@pytest.mark.benchmark
class TestCachePerformance:
    """Performance benchmarks for cache operations."""

    def test_cache_set_performance(self, benchmark, cache: ResponseCache) -> None:
        """Benchmark cache set operations."""
        async def set_operation():
            await cache.set('test-key', 'test-value')

        def setup():
            return (), {}

        benchmark.pedantic(
            lambda: asyncio.run(set_operation()),
            setup=setup,
            rounds=100,
            iterations=1,
        )
```

### Performance Assertions

```python
@pytest.mark.asyncio
async def test_concurrent_cache_operations_performance(self, cache: ResponseCache) -> None:
    """Test performance under concurrent access."""
    # ... setup and operations ...
    
    # Performance assertions with reasonable thresholds
    assert set_time < 5.0, f'Concurrent sets took too long: {set_time:.2f}s'
    assert get_time < 2.0, f'Concurrent gets took too long: {get_time:.2f}s'
```

**Pattern**: Use performance assertions with descriptive error messages that include actual timing.

## Test Markers and Organization

### Marker Usage

```python
@pytest.mark.integration    # Real API interactions
@pytest.mark.slow          # Long-running tests
@pytest.mark.benchmark     # Performance benchmarks
@pytest.mark.asyncio       # Async test functions
```

### Running Specific Test Categories

```bash
# Unit tests only
pytest tests/ -m "not integration and not benchmark"

# Integration tests only
pytest tests/ -m "integration"

# Performance benchmarks only
pytest tests/ -m "benchmark"

# All tests except slow ones
pytest tests/ -m "not slow"
```

## Error Handling Testing

### Exception Testing Patterns

```python
# Test specific exception types
with pytest.raises(RegistryAPIError) as exc_info:
    await client.search_servers('test')

# Verify exception details
assert exc_info.value.status_code == 404
assert 'not found' in str(exc_info.value).lower()
```

### Error Boundary Testing

```python
def test_handle_command_error_api_error_server_unavailable(self, capsys) -> None:
    """Test error handling for server unavailable (HTTP 500+)."""
    exc = RegistryAPIError('Internal server error')
    exc.status_code = 500

    result = _handle_command_error(exc)

    captured = capsys.readouterr()
    assert result == 1
    assert 'Error: Registry service unavailable. Please try again later.' in captured.err
```

**Pattern**: Test both the exception handling logic and the user-facing error messages.

## Configuration Testing

### Environment Variable Testing

```python
def test_config_from_env(self, monkeypatch) -> None:
    """Test configuration loading from environment variables."""
    monkeypatch.setenv('MCP_REGISTRY_TIMEOUT', '45.0')
    monkeypatch.setenv('MCP_REGISTRY_MAX_RETRIES', '5')
    
    config = ClientConfig.from_env()
    
    assert config.timeout == 45.0
    assert config.max_retries == 5
```

### Configuration Validation

```python
def test_invalid_config_values(self) -> None:
    """Test handling of invalid configuration values."""
    with pytest.raises(ValueError):
        ClientConfig(timeout=-1.0)  # Negative timeout
    
    with pytest.raises(ValueError):
        ClientConfig(max_retries=-1)  # Negative retries
```

## CLI Testing Patterns

### Command Line Argument Testing

```python
def test_cli_search_real_api(self) -> None:
    """Test CLI search command with real API."""
    result = run_cli_command(['search', 'git'])
    
    assert result.returncode == 0
    assert 'NAME' in result.stdout
    assert 'DESCRIPTION' in result.stdout
    
    # Should have at least some results
    lines = result.stdout.strip().split('\n')
    assert len(lines) > 2  # Header + separator + at least one result
```

### JSON Output Validation

```python
def test_cli_search_json_output_real_api(self) -> None:
    """Test CLI search with JSON output using real API."""
    result = run_cli_command(['--json', 'search', 'git'])
    
    assert result.returncode == 0
    
    # Validate JSON structure
    data = json.loads(result.stdout)
    assert isinstance(data, list)
    
    if data:  # Only validate if results exist
        first_result = data[0]
        assert 'name' in first_result
        assert 'repository' in first_result
```

## Coverage Guidelines

### Target Coverage Levels

- **Overall Coverage**: >90%
- **Core Modules** (`client.py`, `cache.py`): 100%
- **CLI Module**: >95%
- **Models**: 100% (data classes should be fully tested)

### Coverage Exclusions

Use `pragma: no cover` sparingly and only for:

- Debug code that won't run in production
- Platform-specific code that can't be tested in CI
- Defensive code that's difficult to trigger in tests

```python
if __name__ == "__main__":  # pragma: no cover
    main()
```

## Continuous Integration Considerations

### Test Categorization in CI

```yaml
# Example CI configuration
test-unit:
  run: pytest tests/ -m "not integration and not slow"

test-integration:
  run: pytest tests/ -m "integration" --maxfail=5

test-performance:
  run: pytest tests/ -m "benchmark" --benchmark-only
```

### Flaky Test Management

- Use `@pytest.mark.flaky(reruns=3)` for tests that may fail due to external factors
- Implement proper timeouts for network-dependent tests
- Use deterministic test data when possible

## Best Practices Summary

1. **Test Edge Cases**: Always test boundary conditions, error states, and concurrent scenarios
2. **Use Descriptive Names**: Test names should clearly describe what is being tested
3. **Keep Tests Independent**: Each test should be able to run in isolation
4. **Mock External Dependencies**: Use mocks for external APIs in unit tests
5. **Validate Error Conditions**: Test not just success paths but all failure modes
6. **Performance Awareness**: Include performance tests for critical paths
7. **Documentation**: Document complex test setups and unusual patterns
8. **Regular Review**: Periodically review and update test patterns as the codebase evolves

## Tools and Dependencies

- **pytest**: Primary testing framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Coverage reporting
- **pytest-benchmark**: Performance benchmarking
- **pytest-html**: HTML test reports
- **httpx**: HTTP client testing
- **unittest.mock**: Mocking framework

This testing strategy ensures robust, maintainable code with high confidence in production reliability.