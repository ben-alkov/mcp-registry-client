"""Performance tests for cache functionality."""

import asyncio
import sys
import time

import pytest

from mcp_registry_client.cache import CacheEntry, ResponseCache
from mcp_registry_client.config import ClientConfig


@pytest.mark.benchmark
class TestCachePerformance:
    """Performance benchmarks for cache operations."""

    @pytest.fixture
    def config(self) -> ClientConfig:
        """Create test configuration."""
        config = ClientConfig()
        config.cache_ttl = 300  # 5 minutes
        config.enable_cache = True
        return config

    @pytest.fixture
    def cache(self, config: ClientConfig) -> ResponseCache:
        """Create test cache."""
        return ResponseCache(config)

    def test_cache_set_performance(self, benchmark, cache: ResponseCache) -> None:
        """Benchmark cache set operations."""

        async def set_operation() -> None:
            await cache.set('test-key', 'test-value')

        def setup() -> tuple[tuple, dict]:
            return (), {}

        # Benchmark the async operation
        benchmark.pedantic(
            lambda: asyncio.run(set_operation()),
            setup=setup,
            rounds=100,
            iterations=1,
        )

    def test_cache_get_performance(self, benchmark, cache: ResponseCache) -> None:
        """Benchmark cache get operations."""
        # Pre-populate cache
        asyncio.run(cache.set('test-key', 'test-value'))

        async def get_operation() -> str | None:
            return await cache.get('test-key')

        def setup() -> tuple[tuple, dict]:
            return (), {}

        # Benchmark the async operation
        result = benchmark.pedantic(
            lambda: asyncio.run(get_operation()),
            setup=setup,
            rounds=100,
            iterations=1,
        )
        assert result == 'test-value'

    def test_cache_miss_performance(self, benchmark, cache: ResponseCache) -> None:
        """Benchmark cache miss operations."""

        async def get_missing_operation() -> str | None:
            return await cache.get('nonexistent-key')

        def setup() -> tuple[tuple, dict]:
            return (), {}

        # Benchmark the async operation
        result = benchmark.pedantic(
            lambda: asyncio.run(get_missing_operation()),
            setup=setup,
            rounds=100,
            iterations=1,
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_concurrent_cache_operations_performance(
        self, cache: ResponseCache
    ) -> None:
        """Test performance under concurrent access."""
        num_operations = 1000
        keys = [f'key-{i}' for i in range(num_operations)]
        values = [f'value-{i}' for i in range(num_operations)]

        # Measure time for concurrent set operations
        start_time = time.time()

        async def set_value(key: str, value: str) -> None:
            await cache.set(key, value)

        # Run concurrent sets
        await asyncio.gather(*[set_value(k, v) for k, v in zip(keys, values, strict=True)])

        set_time = time.time() - start_time

        # Measure time for concurrent get operations
        start_time = time.time()

        async def get_value(key: str) -> str | None:
            return await cache.get(key)

        # Run concurrent gets
        results = await asyncio.gather(*[get_value(k) for k in keys])

        get_time = time.time() - start_time

        # Verify all operations completed successfully
        assert len(results) == num_operations
        assert all(r is not None for r in results)

        # Performance assertions (these are somewhat arbitrary but reasonable)
        assert set_time < 5.0, f'Concurrent sets took too long: {set_time:.2f}s'
        assert get_time < 2.0, f'Concurrent gets took too long: {get_time:.2f}s'

        # Verify cache contains all items
        assert len(cache._cache) == num_operations

    @pytest.mark.asyncio
    async def test_cache_cleanup_performance(self, cache: ResponseCache) -> None:
        """Test performance of cache cleanup operations."""
        # Pre-populate cache with expired items
        num_items = 1000

        # Add items with very short TTL that will expire immediately

        for i in range(num_items):
            # Create expired cache entries
            entry = CacheEntry(
                f'value-{i}', ttl=-1
            )  # Negative TTL makes it immediately expired
            cache._cache[f'key-{i}'] = entry

        # Measure cleanup time
        start_time = time.time()
        await cache.cleanup_expired()
        cleanup_time = time.time() - start_time

        # Should complete quickly even with many expired items
        assert cleanup_time < 1.0, f'Cleanup took too long: {cleanup_time:.2f}s'

        # All expired items should be removed
        assert len(cache._cache) == 0

    def test_cache_memory_usage_pattern(self, cache: ResponseCache) -> None:
        """Test cache memory usage patterns."""
        # Measure baseline memory
        baseline_size = sys.getsizeof(cache._cache)

        # Add many items to cache
        num_items = 10000
        for i in range(num_items):
            asyncio.run(cache.set(f'key-{i}', f'value-{i}' * 100))  # Larger values

        # Measure cache size after population
        populated_size = sys.getsizeof(cache._cache)

        # Calculate memory per item (rough estimate)
        memory_per_item = (populated_size - baseline_size) / num_items

        # Should be reasonable memory usage per item
        assert memory_per_item < 1000, f'Memory per item too high: {memory_per_item} bytes'

    @pytest.mark.asyncio
    async def test_cache_ttl_expiration_performance(self, cache: ResponseCache) -> None:
        """Test performance of TTL-based expiration."""
        # Set items with very short TTL
        cache.ttl = 1  # 1 second TTL

        num_items = 100
        for i in range(num_items):
            await cache.set(f'key-{i}', f'value-{i}')

        # All items should be present initially
        assert len(cache._cache) == num_items

        # Wait for expiration
        await asyncio.sleep(1.1)

        # Measure time to detect and handle expiration
        start_time = time.time()

        # Accessing any key should trigger cleanup of expired items
        result = await cache.get('key-0')

        expiration_time = time.time() - start_time

        # Should handle expiration quickly
        assert expiration_time < 0.5, (
            f'Expiration handling took too long: {expiration_time:.2f}s'
        )

        # Item should be expired (None result)
        assert result is None
