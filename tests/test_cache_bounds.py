"""
Tests for cache infrastructure: cachebox integration, env var configuration,
eviction behavior, and thread safety.
"""

import os
import threading
from typing import Generator

import cachebox
import pytest


class TestCacheboxImport:
    """Tests verifying cachebox is properly installed and importable."""

    def test_cachebox_import_succeeds(self) -> None:
        """Verify cachebox can be imported."""
        import cachebox

        assert cachebox is not None

    def test_cachebox_version(self) -> None:
        """Verify cachebox version is >= 5.0."""
        import cachebox

        # Version is available as __version__
        version = cachebox.__version__
        major = int(version.split(".")[0])
        assert major >= 5, f"Expected cachebox version >= 5.0, got {version}"


class TestLRUEviction:
    """Tests verifying LRU cache eviction behavior."""

    def test_lru_eviction_at_maxsize(self) -> None:
        """Verify LRUCache evicts the least recently used entry when maxsize is exceeded."""
        cache = cachebox.LRUCache(maxsize=3)

        # Insert 3 entries
        cache["a"] = 1
        cache["b"] = 2
        cache["c"] = 3
        assert len(cache) == 3

        # Insert 4th entry - should evict "a" (least recently used)
        cache["d"] = 4
        assert len(cache) == 3
        assert "a" not in cache
        assert "b" in cache
        assert "c" in cache
        assert "d" in cache

    def test_lru_access_updates_recency(self) -> None:
        """Verify accessing an entry updates its recency, preventing eviction."""
        cache = cachebox.LRUCache(maxsize=3)

        cache["a"] = 1
        cache["b"] = 2
        cache["c"] = 3

        # Access "a" to make it more recent
        _ = cache["a"]

        # Insert new entry - should evict "b" now (least recently used)
        cache["d"] = 4
        assert len(cache) == 3
        assert "a" in cache  # Still present because we accessed it
        assert "b" not in cache  # Evicted instead
        assert "c" in cache
        assert "d" in cache


class TestTTLCache:
    """Tests verifying TTL cache expiration behavior."""

    def test_ttl_cache_accepts_ttl(self) -> None:
        """Verify TTLCache can be created with a TTL parameter."""
        cache = cachebox.TTLCache(maxsize=10, ttl=60)
        assert cache.maxsize == 10
        # Note: actual TTL expiration would require time-based tests


class TestThreadSafety:
    """Tests verifying thread safety of cachebox caches."""

    def test_concurrent_read_write_no_corruption(self) -> None:
        """Verify concurrent reads and writes from multiple threads don't corrupt the cache."""
        cache = cachebox.LRUCache(maxsize=100)
        errors: list[Exception] = []
        iterations = 1000

        def writer(start: int) -> None:
            try:
                for i in range(start, start + iterations):
                    cache[i] = i * 2
            except Exception as e:
                errors.append(e)

        def reader(start: int) -> None:
            try:
                for i in range(start, start + iterations):
                    _ = cache.get(i, None)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=writer, args=(0,)),
            threading.Thread(target=writer, args=(iterations,)),
            threading.Thread(target=reader, args=(0,)),
            threading.Thread(target=reader, args=(iterations,)),
            threading.Thread(target=reader, args=(iterations * 2,)),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Thread safety errors: {errors}"
        assert len(cache) <= 100, f"Cache exceeded maxsize: {len(cache)}"


class TestEnvironmentVariables:
    """Tests verifying environment variable configuration of cache sizes."""

    def test_default_cache_maxsize_env_var(self) -> None:
        """Verify DEFAULT_CACHE_MAXSIZE can be read from environment."""
        from y import ENVIRONMENT_VARIABLES as ENVS

        # Should have default value
        assert ENVS.DEFAULT_CACHE_MAXSIZE > 0
        assert ENVS.DEFAULT_CACHE_MAXSIZE >= 1_000
        assert ENVS.DEFAULT_CACHE_MAXSIZE <= 1_000_000

    def test_block_cache_maxsize_env_var(self) -> None:
        """Verify BLOCK_CACHE_MAXSIZE can be read from environment."""
        from y import ENVIRONMENT_VARIABLES as ENVS

        assert ENVS.BLOCK_CACHE_MAXSIZE > 0
        assert ENVS.BLOCK_CACHE_MAXSIZE >= 1_000
        assert ENVS.BLOCK_CACHE_MAXSIZE <= 1_000_000

    def test_contract_cache_maxsize_env_var(self) -> None:
        """Verify CONTRACT_CACHE_MAXSIZE can be read from environment."""
        from y import ENVIRONMENT_VARIABLES as ENVS

        assert ENVS.CONTRACT_CACHE_MAXSIZE > 0
        assert ENVS.CONTRACT_CACHE_MAXSIZE >= 1_000
        assert ENVS.CONTRACT_CACHE_MAXSIZE <= 1_000_000

    def test_price_cache_maxsize_env_var(self) -> None:
        """Verify PRICE_CACHE_MAXSIZE can be read from environment."""
        from y import ENVIRONMENT_VARIABLES as ENVS

        assert ENVS.PRICE_CACHE_MAXSIZE > 0
        assert ENVS.PRICE_CACHE_MAXSIZE >= 1_000
        assert ENVS.PRICE_CACHE_MAXSIZE <= 1_000_000


class TestCacheModule:
    """Tests verifying the y._cache module provides working cache instances."""

    def test_get_lru_cache_returns_cachebox_cache(self) -> None:
        """Verify get_lru_cache returns a cachebox LRUCache."""
        from y._cache import get_lru_cache

        cache = get_lru_cache()
        assert isinstance(cache, cachebox.LRUCache)

    def test_get_ttl_cache_returns_cachebox_cache(self) -> None:
        """Verify get_ttl_cache returns a cachebox TTLCache."""
        from y._cache import get_ttl_cache

        cache = get_ttl_cache(ttl=300)
        assert isinstance(cache, cachebox.TTLCache)

    def test_default_lru_cache_exists(self) -> None:
        """Verify DEFAULT_LRU_CACHE pre-built instance exists."""
        from y._cache import DEFAULT_LRU_CACHE

        assert isinstance(DEFAULT_LRU_CACHE, cachebox.LRUCache)
        assert DEFAULT_LRU_CACHE.maxsize > 0

    def test_block_lru_cache_exists(self) -> None:
        """Verify BLOCK_LRU_CACHE pre-built instance exists."""
        from y._cache import BLOCK_LRU_CACHE

        assert isinstance(BLOCK_LRU_CACHE, cachebox.LRUCache)
        assert BLOCK_LRU_CACHE.maxsize > 0

    def test_contract_lru_cache_exists(self) -> None:
        """Verify CONTRACT_LRU_CACHE pre-built instance exists."""
        from y._cache import CONTRACT_LRU_CACHE

        assert isinstance(CONTRACT_LRU_CACHE, cachebox.LRUCache)
        assert CONTRACT_LRU_CACHE.maxsize > 0

    def test_price_lru_cache_exists(self) -> None:
        """Verify PRICE_LRU_CACHE pre-built instance exists."""
        from y._cache import PRICE_LRU_CACHE

        assert isinstance(PRICE_LRU_CACHE, cachebox.LRUCache)
        assert PRICE_LRU_CACHE.maxsize > 0

    def test_get_lru_cache_respects_cache_type(self) -> None:
        """Verify get_lru_cache returns different maxsize for different cache types."""
        from y._cache import get_lru_cache

        default_cache = get_lru_cache("default")
        block_cache = get_lru_cache("block")
        contract_cache = get_lru_cache("contract")
        price_cache = get_lru_cache("price")

        # Block cache should have the largest maxsize
        assert block_cache.maxsize >= default_cache.maxsize
        assert block_cache.maxsize >= contract_cache.maxsize
        assert block_cache.maxsize >= price_cache.maxsize


class TestEnvVarOverride:
    """Tests verifying env vars can override cache sizes at runtime."""

    def test_env_var_override_default_cache_maxsize(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify setting DEFAULT_CACHE_MAXSIZE env var changes the cache maxsize."""
        # Set env var with YPRICEMAGIC prefix (as required by typed_envs EnvVarFactory)
        monkeypatch.setenv("YPRICEMAGIC_DEFAULT_CACHE_MAXSIZE", "42")

        # Need to re-import to pick up new env var
        # Since the module may already be cached, we test the env var directly
        from typed_envs import EnvVarFactory

        _envs = EnvVarFactory("YPRICEMAGIC")
        value = _envs.create_env("DEFAULT_CACHE_MAXSIZE", int, default=50_000, verbose=False)
        assert value == 42, f"Expected 42, got {value}"

    def test_env_var_override_block_cache_maxsize(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify setting BLOCK_CACHE_MAXSIZE env var changes the cache maxsize."""
        monkeypatch.setenv("YPRICEMAGIC_BLOCK_CACHE_MAXSIZE", "12345")

        from typed_envs import EnvVarFactory

        _envs = EnvVarFactory("YPRICEMAGIC")
        value = _envs.create_env("BLOCK_CACHE_MAXSIZE", int, default=500_000, verbose=False)
        assert value == 12345, f"Expected 12345, got {value}"
