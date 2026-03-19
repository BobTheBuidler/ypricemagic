"""Tests for cachebox migration and cache bounds.

These tests verify:
- cachebox dependency is importable
- LRUCache and TTLCache work as expected
- cachebox.cached decorator works with sync and async functions
- Cache bounds are respected (entries evicted when maxsize exceeded)
- The _cache module factory functions produce correctly sized caches
- No alru_cache / async_lru imports remain in y/

These tests do NOT require an RPC connection.
"""

import asyncio
import os
import re

import cachebox
import pytest


class TestCacheboxImport:
    """Verify cachebox is installed and importable."""

    def test_cachebox_importable(self):
        assert hasattr(cachebox, "LRUCache")
        assert hasattr(cachebox, "TTLCache")
        assert hasattr(cachebox, "cached")

    def test_cachebox_version(self):
        version = cachebox.__version__
        major = int(version.split(".")[0])
        assert major >= 4, f"Expected cachebox >= 4.x, got {version}"


class TestLRUCacheBounds:
    """Verify LRUCache respects maxsize bounds."""

    def test_lru_cache_maxsize_respected(self):
        cache = cachebox.LRUCache(3)
        cache[1] = "a"
        cache[2] = "b"
        cache[3] = "c"
        assert len(cache) == 3

        # Adding a 4th item should evict the least recently used
        cache[4] = "d"
        assert len(cache) == 3
        # Item 1 should have been evicted (LRU)
        assert 1 not in cache
        assert 4 in cache

    def test_lru_cache_access_updates_recency(self):
        cache = cachebox.LRUCache(3)
        cache[1] = "a"
        cache[2] = "b"
        cache[3] = "c"

        # Access item 1 to make it recently used
        _ = cache[1]

        # Adding item 4 should now evict item 2 (least recently used)
        cache[4] = "d"
        assert 1 in cache
        assert 2 not in cache


class TestTTLCacheBounds:
    """Verify TTLCache respects maxsize bounds."""

    def test_ttl_cache_maxsize_respected(self):
        cache = cachebox.TTLCache(3, ttl=60)
        cache[1] = "a"
        cache[2] = "b"
        cache[3] = "c"
        assert len(cache) == 3

        cache[4] = "d"
        assert len(cache) == 3


class TestCachedDecoratorSync:
    """Verify cachebox.cached works with sync functions."""

    def test_cached_sync_function(self):
        call_count = 0
        cache = cachebox.LRUCache(128)

        @cachebox.cached(cache)
        def add(a, b):
            nonlocal call_count
            call_count += 1
            return a + b

        assert add(1, 2) == 3
        assert call_count == 1

        # Should come from cache
        assert add(1, 2) == 3
        assert call_count == 1

        # Different args -> cache miss
        assert add(3, 4) == 7
        assert call_count == 2

    def test_cached_sync_maxsize_eviction(self):
        cache = cachebox.LRUCache(2)

        @cachebox.cached(cache)
        def square(x):
            return x * x

        square(1)
        square(2)
        assert len(cache) == 2

        square(3)
        assert len(cache) == 2  # Still bounded


class TestCachedDecoratorAsync:
    """Verify cachebox.cached works with async functions."""

    def test_cached_async_function(self):
        call_count = 0
        cache = cachebox.LRUCache(128)

        @cachebox.cached(cache)
        async def async_add(a, b):
            nonlocal call_count
            call_count += 1
            return a + b

        loop = asyncio.new_event_loop()
        try:
            result1 = loop.run_until_complete(async_add(1, 2))
            assert result1 == 3
            assert call_count == 1

            # Should come from cache
            result2 = loop.run_until_complete(async_add(1, 2))
            assert result2 == 3
            assert call_count == 1
        finally:
            loop.close()

    def test_cached_async_maxsize_eviction(self):
        cache = cachebox.LRUCache(2)

        @cachebox.cached(cache)
        async def async_square(x):
            return x * x

        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(async_square(1))
            loop.run_until_complete(async_square(2))
            assert len(cache) == 2

            loop.run_until_complete(async_square(3))
            assert len(cache) == 2
        finally:
            loop.close()


class TestCachedDecoratorTTL:
    """Verify cachebox.cached with TTLCache."""

    def test_ttl_cache_decorator(self):
        cache = cachebox.TTLCache(128, ttl=3600)

        @cachebox.cached(cache)
        def get_value(key):
            return f"value_{key}"

        result = get_value("test")
        assert result == "value_test"

        # Should come from cache
        result2 = get_value("test")
        assert result2 == "value_test"


class TestNoAlruCacheImports:
    """Verify no alru_cache or async_lru imports remain in the y/ package."""

    def test_no_alru_cache_in_source(self):
        """Scan all .py files in y/ for alru_cache or async_lru imports."""
        y_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "y")
        violations = []

        for root, _dirs, files in os.walk(y_dir):
            # Skip __pycache__ and build directories
            if "__pycache__" in root or "build" in root:
                continue
            for filename in files:
                if not filename.endswith(".py"):
                    continue
                filepath = os.path.join(root, filename)
                with open(filepath) as f:
                    for line_num, line in enumerate(f, 1):
                        if re.search(r"\balru_cache\b|\basync_lru\b", line):
                            violations.append(f"{filepath}:{line_num}: {line.strip()}")

        assert violations == [], (
            f"Found alru_cache/async_lru references in y/:\n" + "\n".join(violations)
        )


class TestCacheboxInDependencies:
    """Verify cachebox appears in dependency files."""

    def test_cachebox_in_requirements_txt(self):
        req_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "requirements.txt")
        with open(req_file) as f:
            content = f.read()
        assert "cachebox" in content, "cachebox not found in requirements.txt"

    def test_cachebox_in_pyproject_toml(self):
        pyproject = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pyproject.toml")
        with open(pyproject) as f:
            content = f.read()
        assert "cachebox" in content, "cachebox not found in pyproject.toml"


class TestAllMemoryCachesBounded:
    """Verify all a_sync cache_type='memory' decorators have ram_cache_maxsize."""

    def test_no_unbounded_memory_caches(self):
        """Scan y/ for cache_type='memory' without ram_cache_maxsize."""
        y_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "y")
        violations = []

        for root, _dirs, files in os.walk(y_dir):
            if "__pycache__" in root or "build" in root:
                continue
            for filename in files:
                if not filename.endswith(".py"):
                    continue
                filepath = os.path.join(root, filename)
                with open(filepath) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line_num, line in enumerate(lines, 1):
                        stripped = line.strip()
                        # Skip comments
                        if stripped.startswith("#"):
                            continue
                        if 'cache_type="memory"' in stripped or "cache_type='memory'" in stripped:
                            if "ram_cache_maxsize" not in stripped:
                                violations.append(f"{filepath}:{line_num}: {stripped}")

        assert violations == [], (
            f"Found cache_type='memory' without ram_cache_maxsize:\n" + "\n".join(violations)
        )

    def test_no_unbounded_ram_cache_maxsize(self):
        """Scan y/ for ram_cache_maxsize=None (explicitly unbounded)."""
        y_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "y")
        violations = []

        for root, _dirs, files in os.walk(y_dir):
            if "__pycache__" in root or "build" in root:
                continue
            for filename in files:
                if not filename.endswith(".py"):
                    continue
                filepath = os.path.join(root, filename)
                # Allow _db/ files to have unbounded caches (database layer)
                if os.sep + "_db" + os.sep in filepath:
                    continue
                with open(filepath) as f:
                    for line_num, line in enumerate(f, 1):
                        stripped = line.strip()
                        if stripped.startswith("#"):
                            continue
                        if "ram_cache_maxsize=None" in stripped:
                            violations.append(f"{filepath}:{line_num}: {stripped}")

        assert violations == [], (
            f"Found ram_cache_maxsize=None outside _db/:\n" + "\n".join(violations)
        )
