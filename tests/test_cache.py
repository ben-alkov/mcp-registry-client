"""Tests for the response cache."""

import asyncio
from unittest.mock import Mock, patch

import pytest

from mcp_registry_client.cache import CacheEntry, ResponseCache
from mcp_registry_client.config import ClientConfig


class TestCacheEntry:
    """Tests for CacheEntry."""

    def test_init(self) -> None:
        """Test cache entry initialization."""
        value = 'test-value'
        ttl = 300

        with patch('time.time', return_value=1000.0):
            entry = CacheEntry(value, ttl)

        assert entry.value == value
        assert entry.expires_at == 1300.0  # 1000 + 300

    def test_is_expired_false(self) -> None:
        """Test is_expired returns False when not expired."""
        with patch('time.time', return_value=1000.0):
            entry = CacheEntry('value', 300)

        # Check before expiration
        with patch('time.time', return_value=1200.0):  # 100 seconds later
            assert not entry.is_expired()

    def test_is_expired_true(self) -> None:
        """Test is_expired returns True when expired."""
        with patch('time.time', return_value=1000.0):
            entry = CacheEntry('value', 300)

        # Check after expiration
        with patch('time.time', return_value=1301.0):  # 301 seconds later
            assert entry.is_expired()

    def test_is_expired_exact_boundary(self) -> None:
        """Test is_expired at exact expiration boundary."""
        with patch('time.time', return_value=1000.0):
            entry = CacheEntry('value', 300)

        # Check at exact expiration time
        with patch('time.time', return_value=1300.0):  # Exactly 300 seconds later
            assert not entry.is_expired()

        # Check just after expiration time
        with patch('time.time', return_value=1300.1):  # 0.1 seconds after expiration
            assert entry.is_expired()


class TestResponseCache:
    """Tests for ResponseCache."""

    def test_init_enabled(self) -> None:
        """Test cache initialization when enabled."""
        config = Mock(spec=ClientConfig)
        config.enable_cache = True
        config.cache_ttl = 600

        cache = ResponseCache(config)

        assert cache.enabled is True
        assert cache.ttl == 600
        assert cache._cache == {}

    def test_init_disabled(self) -> None:
        """Test cache initialization when disabled."""
        config = Mock(spec=ClientConfig)
        config.enable_cache = False
        config.cache_ttl = 600

        cache = ResponseCache(config)

        assert cache.enabled is False
        assert cache.ttl == 600

    @pytest.mark.asyncio
    async def test_get_cache_disabled(self) -> None:
        """Test get returns None when cache is disabled."""
        config = Mock(spec=ClientConfig)
        config.enable_cache = False
        config.cache_ttl = 300

        cache = ResponseCache(config)

        result = await cache.get('test-key')
        assert result is None

    @pytest.mark.asyncio
    async def test_set_cache_disabled(self) -> None:
        """Test set does nothing when cache is disabled."""
        config = Mock(spec=ClientConfig)
        config.enable_cache = False
        config.cache_ttl = 300

        cache = ResponseCache(config)

        await cache.set('test-key', 'test-value')
        # Should not store anything
        assert cache._cache == {}

    @pytest.mark.asyncio
    async def test_get_missing_key(self) -> None:
        """Test get returns None for missing key."""
        config = Mock(spec=ClientConfig)
        config.enable_cache = True
        config.cache_ttl = 300

        cache = ResponseCache(config)

        result = await cache.get('missing-key')
        assert result is None

    @pytest.mark.asyncio
    async def test_set_and_get_success(self) -> None:
        """Test successful set and get operations."""
        config = Mock(spec=ClientConfig)
        config.enable_cache = True
        config.cache_ttl = 300

        cache = ResponseCache(config)

        test_value = {'data': 'test'}
        await cache.set('test-key', test_value)

        result = await cache.get('test-key')
        assert result == test_value

    @pytest.mark.asyncio
    async def test_get_expired_entry(self) -> None:
        """Test get returns None and removes expired entry."""
        config = Mock(spec=ClientConfig)
        config.enable_cache = True
        config.cache_ttl = 300

        cache = ResponseCache(config)

        with patch('time.time', return_value=1000.0):
            await cache.set('test-key', 'test-value')

        # Fast forward past expiration
        with patch('time.time', return_value=1301.0):
            result = await cache.get('test-key')

        assert result is None
        # Entry should be removed from cache
        assert 'test-key' not in cache._cache

    @pytest.mark.asyncio
    async def test_clear(self) -> None:
        """Test clear removes all entries."""
        config = Mock(spec=ClientConfig)
        config.enable_cache = True
        config.cache_ttl = 300

        cache = ResponseCache(config)

        await cache.set('key1', 'value1')
        await cache.set('key2', 'value2')

        assert len(cache._cache) == 2

        await cache.clear()

        assert len(cache._cache) == 0

    @pytest.mark.asyncio
    async def test_cleanup_expired_cache_disabled(self) -> None:
        """Test cleanup_expired does nothing when cache disabled."""
        config = Mock(spec=ClientConfig)
        config.enable_cache = False
        config.cache_ttl = 300

        cache = ResponseCache(config)

        # Manually add entry to test that cleanup doesn't run
        cache._cache['test-key'] = Mock()

        await cache.cleanup_expired()

        # Entry should still be there since cache is disabled
        assert 'test-key' in cache._cache

    @pytest.mark.asyncio
    async def test_cleanup_expired_removes_expired_only(self) -> None:
        """Test cleanup_expired removes only expired entries."""
        config = Mock(spec=ClientConfig)
        config.enable_cache = True
        config.cache_ttl = 300

        cache = ResponseCache(config)

        with patch('time.time', return_value=1000.0):
            await cache.set('fresh-key', 'fresh-value')
            await cache.set('old-key', 'old-value')

        # Fast forward to make one entry expired
        with patch('time.time', return_value=1200.0):
            # Manually expire one entry by modifying its expiration time
            cache._cache['old-key'].expires_at = 1100.0

            await cache.cleanup_expired()

        # Fresh entry should remain, old entry should be removed
        assert 'fresh-key' in cache._cache
        assert 'old-key' not in cache._cache

    @pytest.mark.asyncio
    async def test_cleanup_expired_no_expired_entries(self) -> None:
        """Test cleanup_expired when no entries are expired."""
        config = Mock(spec=ClientConfig)
        config.enable_cache = True
        config.cache_ttl = 300

        cache = ResponseCache(config)

        await cache.set('key1', 'value1')
        await cache.set('key2', 'value2')

        original_count = len(cache._cache)

        await cache.cleanup_expired()

        # All entries should remain
        assert len(cache._cache) == original_count

    def test_cache_key_for_search(self) -> None:
        """Test cache key generation for search requests."""
        config = Mock(spec=ClientConfig)
        config.enable_cache = True
        config.cache_ttl = 300

        cache = ResponseCache(config)

        # Test normal case
        key = cache.cache_key_for_search('Test-Name')
        assert key == 'search:test-name'

        # Test with whitespace
        key = cache.cache_key_for_search('  Test Name  ')
        assert key == 'search:test name'

    def test_cache_key_for_server(self) -> None:
        """Test cache key generation for server requests."""
        config = Mock(spec=ClientConfig)
        config.enable_cache = True
        config.cache_ttl = 300

        cache = ResponseCache(config)

        key = cache.cache_key_for_server('server-123')
        assert key == 'server:server-123'

    def test_cache_key_for_server_by_name(self) -> None:
        """Test cache key generation for server by name requests."""
        config = Mock(spec=ClientConfig)
        config.enable_cache = True
        config.cache_ttl = 300

        cache = ResponseCache(config)

        # Test normal case
        key = cache.cache_key_for_server_by_name('Test-Server')
        assert key == 'server_by_name:test-server'

        # Test with whitespace
        key = cache.cache_key_for_server_by_name('  Test Server  ')
        assert key == 'server_by_name:test server'


class TestResponseCacheEdgeCases:
    """Edge case tests for ResponseCache."""

    @pytest.mark.asyncio
    async def test_concurrent_access_same_key(self) -> None:
        """Test concurrent access to the same cache key."""
        config = Mock(spec=ClientConfig)
        config.enable_cache = True
        config.cache_ttl = 300

        cache = ResponseCache(config)

        # Test concurrent sets
        async def set_value(key: str, value: str) -> None:
            await cache.set(key, value)

        # Run multiple sets concurrently
        await asyncio.gather(
            set_value('test-key', 'value1'),
            set_value('test-key', 'value2'),
            set_value('test-key', 'value3'),
        )

        # Should have exactly one entry
        assert len(cache._cache) == 1
        result = await cache.get('test-key')
        # Result should be one of the values
        assert result in ['value1', 'value2', 'value3']

    @pytest.mark.asyncio
    async def test_concurrent_get_and_cleanup(self) -> None:
        """Test concurrent get and cleanup operations."""
        config = Mock(spec=ClientConfig)
        config.enable_cache = True
        config.cache_ttl = 300

        cache = ResponseCache(config)

        await cache.set('test-key', 'test-value')

        # Run get and cleanup concurrently
        results = await asyncio.gather(
            cache.get('test-key'), cache.cleanup_expired(), return_exceptions=True
        )

        # Should not raise exceptions
        assert not any(isinstance(r, Exception) for r in results)

    @pytest.mark.asyncio
    async def test_zero_ttl(self) -> None:
        """Test cache behavior with zero TTL."""
        config = Mock(spec=ClientConfig)
        config.enable_cache = True
        config.cache_ttl = 0

        cache = ResponseCache(config)

        with patch('time.time', return_value=1000.0):
            await cache.set('test-key', 'test-value')

        # Entry should be immediately expired
        with patch('time.time', return_value=1000.1):
            result = await cache.get('test-key')

        assert result is None

    @pytest.mark.asyncio
    async def test_negative_ttl(self) -> None:
        """Test cache behavior with negative TTL."""
        config = Mock(spec=ClientConfig)
        config.enable_cache = True
        config.cache_ttl = -100

        cache = ResponseCache(config)

        with patch('time.time', return_value=1000.0):
            await cache.set('test-key', 'test-value')

        # Entry should be immediately expired (expires_at = 900.0)
        result = await cache.get('test-key')
        assert result is None

    @pytest.mark.asyncio
    async def test_very_large_ttl(self) -> None:
        """Test cache behavior with very large TTL."""
        config = Mock(spec=ClientConfig)
        config.enable_cache = True
        config.cache_ttl = 2**31 - 1  # Max 32-bit int

        cache = ResponseCache(config)

        await cache.set('test-key', 'test-value')
        result = await cache.get('test-key')

        assert result == 'test-value'

    @pytest.mark.asyncio
    async def test_cache_none_values(self) -> None:
        """Test caching None values."""
        config = Mock(spec=ClientConfig)
        config.enable_cache = True
        config.cache_ttl = 300

        cache = ResponseCache(config)

        await cache.set('test-key', None)
        result = await cache.get('test-key')

        assert result is None
        # Should distinguish between cached None and missing key
        assert 'test-key' in cache._cache

    @pytest.mark.asyncio
    async def test_cache_complex_objects(self) -> None:
        """Test caching complex nested objects."""
        config = Mock(spec=ClientConfig)
        config.enable_cache = True
        config.cache_ttl = 300

        cache = ResponseCache(config)

        complex_value = {
            'list': [1, 2, 3],
            'dict': {'nested': {'deeply': 'value'}},
            'tuple': (1, 2),
            'none': None,
            'bool': True,
        }

        await cache.set('complex-key', complex_value)
        result = await cache.get('complex-key')

        assert result == complex_value

    @pytest.mark.asyncio
    async def test_many_entries_performance(self) -> None:
        """Test cache performance with many entries."""
        config = Mock(spec=ClientConfig)
        config.enable_cache = True
        config.cache_ttl = 300

        cache = ResponseCache(config)

        # Add many entries
        num_entries = 1000
        for i in range(num_entries):
            await cache.set(f'key-{i}', f'value-{i}')

        assert len(cache._cache) == num_entries

        # Test retrieval
        result = await cache.get('key-500')
        assert result == 'value-500'

        # Test cleanup
        await cache.cleanup_expired()
        # All entries should still be there (not expired)
        assert len(cache._cache) == num_entries

    @pytest.mark.asyncio
    async def test_cleanup_with_mixed_expiration_times(self) -> None:
        """Test cleanup with entries having different expiration times."""
        config = Mock(spec=ClientConfig)
        config.enable_cache = True
        config.cache_ttl = 300

        cache = ResponseCache(config)

        # Add entries at different times
        with patch('time.time', return_value=1000.0):
            await cache.set('old-key', 'old-value')

        with patch('time.time', return_value=1100.0):
            await cache.set('medium-key', 'medium-value')

        with patch('time.time', return_value=1200.0):
            await cache.set('new-key', 'new-value')

        # Cleanup at time when only old entry is expired
        with patch('time.time', return_value=1301.0):  # old-key expires at 1300
            await cache.cleanup_expired()

        assert 'old-key' not in cache._cache
        assert 'medium-key' in cache._cache
        assert 'new-key' in cache._cache

    @pytest.mark.asyncio
    async def test_empty_cache_operations(self) -> None:
        """Test operations on empty cache."""
        config = Mock(spec=ClientConfig)
        config.enable_cache = True
        config.cache_ttl = 300

        cache = ResponseCache(config)

        # All operations on empty cache should work
        result = await cache.get('any-key')
        assert result is None

        await cache.cleanup_expired()  # Should not raise

        await cache.clear()  # Should not raise

        assert len(cache._cache) == 0
