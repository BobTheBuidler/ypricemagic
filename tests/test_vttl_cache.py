"""Tests for the VTTLCache integration used in y/prices/magic.py.

These tests exercise cachebox.VTTLCache directly (without importing the full
y module) to verify per-key TTL, maxsize eviction, skip_cache bypass, and
correct use of ``insert()`` for finite TTL entries.
"""

import asyncio
import os
import time
from functools import wraps

import pytest
from cachebox import VTTLCache

# ---------------------------------------------------------------------------
# Helpers – a minimal replica of __vttl_cache for isolated testing
# ---------------------------------------------------------------------------


def _make_cached_fn(cache_ttl: int = 3600, amount_cache_ttl: int = 300, maxsize: int = 100):
    """Build a toy cached async function that mirrors __vttl_cache semantics."""
    _cache = VTTLCache(maxsize=maxsize)
    call_count = 0

    async def _inner(
        token,
        *,
        block=0,
        fail_to_None=False,
        skip_cache=False,
        ignore_pools=(),
        silent=False,
        amount=None,
    ):
        nonlocal call_count
        call_count += 1
        # Return a simple fake price
        return {"price": 42.0, "token": token, "amount": amount}

    @wraps(_inner)
    async def cache_wrap(
        token,
        *,
        block=0,
        fail_to_None=False,
        skip_cache=False,
        ignore_pools=(),
        silent=False,
        amount=None,
    ):
        if skip_cache:
            return await _inner(
                token,
                block=block,
                fail_to_None=fail_to_None,
                skip_cache=skip_cache,
                ignore_pools=ignore_pools,
                silent=silent,
                amount=amount,
            )

        key = (token, block, fail_to_None, skip_cache, ignore_pools, silent, amount)
        try:
            return _cache[key]
        except KeyError:
            pass

        result = await _inner(
            token,
            block=block,
            fail_to_None=fail_to_None,
            skip_cache=skip_cache,
            ignore_pools=ignore_pools,
            silent=silent,
            amount=amount,
        )
        if result is not None:
            ttl = amount_cache_ttl if amount is not None else cache_ttl
            _cache.insert(key, result, ttl=ttl)
        return result

    cache_wrap.cache = _cache
    cache_wrap.get_call_count = lambda: call_count
    return cache_wrap


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestVTTLCachePerKeyTTL:
    """Verify that per-key TTL works: short-TTL entries expire while long-TTL entries persist."""

    def test_short_ttl_expires_long_ttl_persists(self):
        cache = VTTLCache(maxsize=100)
        cache.insert("short", "value-short", ttl=1)
        cache.insert("long", "value-long", ttl=60)

        # Both should be present immediately
        assert cache["short"] == "value-short"
        assert cache["long"] == "value-long"

        # Wait for short TTL to expire
        time.sleep(1.5)

        with pytest.raises(KeyError):
            _ = cache["short"]

        # Long TTL should still be present
        assert cache["long"] == "value-long"


class TestVTTLCacheMaxsizeEviction:
    """Verify that VTTLCache respects maxsize."""

    def test_maxsize_eviction(self):
        cache = VTTLCache(maxsize=3)
        for i in range(5):
            cache.insert(f"key-{i}", f"val-{i}", ttl=60)

        # Cache should not exceed maxsize
        assert len(cache) <= 3


class TestAmountCacheTTLConfigurable:
    """Verify that AMOUNT_CACHE_TTL env var is declared and configurable."""

    def test_env_var_exists_with_default(self):
        # Load the env module file directly to bypass y/__init__ (dank_mids)
        import importlib.util
        from pathlib import Path

        env_path = Path(__file__).resolve().parent.parent / "y" / "ENVIRONMENT_VARIABLES.py"
        spec = importlib.util.spec_from_file_location("_env_vars", str(env_path))
        ENVS = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ENVS)

        assert hasattr(ENVS, "AMOUNT_CACHE_TTL")
        # If not overridden, the default should be 300
        if "YPRICEMAGIC_AMOUNT_CACHE_TTL" not in os.environ:
            assert int(ENVS.AMOUNT_CACHE_TTL) == 300


class TestSpotAndAmountCoexist:
    """Spot (amount=None) and amount entries with same (token, block) coexist as separate keys."""

    def test_separate_cache_keys(self):
        fn = _make_cached_fn()
        token = "0xABC"

        spot_result = asyncio.run(fn(token, block=100, amount=None))
        amount_result = asyncio.run(fn(token, block=100, amount=1000))

        # Both calls should have hit the inner function (call_count == 2)
        assert fn.get_call_count() == 2

        # Both should be cached with separate keys
        spot_key = (token, 100, False, False, (), False, None)
        amount_key = (token, 100, False, False, (), False, 1000)

        assert spot_key in fn.cache
        assert amount_key in fn.cache
        assert fn.cache[spot_key]["amount"] is None
        assert fn.cache[amount_key]["amount"] == 1000


class TestSkipCacheBypass:
    """skip_cache=True should bypass the cache entirely."""

    def test_skip_cache_does_not_read_or_write(self):
        fn = _make_cached_fn()
        token = "0xDEF"

        # First call populates cache
        asyncio.run(fn(token, block=1))
        assert fn.get_call_count() == 1
        assert len(fn.cache) == 1

        # Second call with skip_cache should call inner again and not add a new entry
        asyncio.run(fn(token, block=1, skip_cache=True))
        assert fn.get_call_count() == 2
        # Cache size unchanged (skip_cache doesn't write)
        assert len(fn.cache) == 1

    def test_skip_cache_returns_fresh_result(self):
        fn = _make_cached_fn()
        token = "0xGHI"

        result1 = asyncio.run(fn(token, block=1))
        result2 = asyncio.run(fn(token, block=1, skip_cache=True))

        # Both should be valid results
        assert result1 is not None
        assert result2 is not None


class TestEntriesActuallyExpire:
    """Verify that insert() creates entries with finite TTL (not __setitem__ with infinite TTL)."""

    def test_insert_creates_expiring_entries(self):
        cache = VTTLCache(maxsize=100)

        # Use insert with a very short TTL
        cache.insert("expiring", "value", ttl=1)

        assert cache["expiring"] == "value"
        time.sleep(1.5)

        with pytest.raises(KeyError):
            _ = cache["expiring"]

    def test_setitem_creates_non_expiring_entries(self):
        """Demonstrates why we must use insert() and not __setitem__."""
        cache = VTTLCache(maxsize=100)

        # __setitem__ creates entries with infinite TTL
        cache["permanent"] = "value"
        time.sleep(1.5)

        # Entry should still be present (infinite TTL)
        assert cache["permanent"] == "value"

    def test_cached_fn_entries_expire(self):
        """Integration test: entries inserted by the cache wrapper actually expire."""
        fn = _make_cached_fn(cache_ttl=1, amount_cache_ttl=1)
        token = "0xEXP"

        asyncio.run(fn(token, block=1))
        assert fn.get_call_count() == 1

        # Second call should hit cache
        asyncio.run(fn(token, block=1))
        assert fn.get_call_count() == 1

        # Wait for expiry
        time.sleep(1.5)

        # Third call should miss cache and call inner again
        asyncio.run(fn(token, block=1))
        assert fn.get_call_count() == 2


class TestCacheHitAvoidsDuplicateCalls:
    """Cached entries should be returned without calling the inner function again."""

    def test_cache_hit(self):
        fn = _make_cached_fn()
        token = "0xHIT"

        asyncio.run(fn(token, block=1))
        assert fn.get_call_count() == 1

        # Second call with same args should hit cache
        asyncio.run(fn(token, block=1))
        assert fn.get_call_count() == 1  # No additional call
