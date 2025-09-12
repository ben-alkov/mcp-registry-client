"""Response caching for the MCP registry client."""

import asyncio
import time
from typing import Any, TypeVar

from .config import ClientConfig

T = TypeVar('T')


class CacheEntry:
    """Cache entry with expiration support."""

    def __init__(self, value: T, ttl: int) -> None:
        """Initialize cache entry.

        Args:
            value: The cached value
            ttl: Time to live in seconds

        """
        self.value = value
        self.expires_at = time.time() + ttl

    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        return time.time() > self.expires_at


class ResponseCache:
    """In-memory response cache with TTL support."""

    def __init__(self, config: ClientConfig) -> None:
        """Initialize response cache.

        Args:
            config: Client configuration with cache settings

        """
        self.enabled = config.enable_cache
        self.ttl = config.cache_ttl
        self._cache: dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Any | None:  # noqa: ANN401
        """Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value if found and not expired, None otherwise

        """
        if not self.enabled:
            return None

        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None

            if entry.is_expired():
                del self._cache[key]
                return None

            return entry.value

    async def set(self, key: str, value: Any) -> None:  # noqa: ANN401
        """Set a value in the cache.

        Args:
            key: Cache key
            value: Value to cache

        """
        if not self.enabled:
            return

        async with self._lock:
            self._cache[key] = CacheEntry(value, self.ttl)

    async def clear(self) -> None:
        """Clear all cached values."""
        async with self._lock:
            self._cache.clear()

    async def cleanup_expired(self) -> None:
        """Remove expired entries from the cache."""
        if not self.enabled:
            return

        async with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, entry in self._cache.items() if current_time > entry.expires_at
            ]
            for key in expired_keys:
                del self._cache[key]

    def cache_key_for_search(self, name: str) -> str:
        """Generate cache key for search requests.

        Args:
            name: Search name parameter

        Returns:
            Cache key

        """
        return f'search:{name.lower().strip()}'

    def cache_key_for_server(self, server_id: str) -> str:
        """Generate cache key for server requests.

        Args:
            server_id: Server ID

        Returns:
            Cache key

        """
        return f'server:{server_id}'

    def cache_key_for_server_by_name(self, name: str) -> str:
        """Generate cache key for server by name requests.

        Args:
            name: Server name

        Returns:
            Cache key

        """
        return f'server_by_name:{name.lower().strip()}'
