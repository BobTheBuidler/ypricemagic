"""
Central cache configuration module for ypricemagic.

This module provides pre-configured cachebox cache instances and factory functions
keyed to environment variable values. All cache sizes are configurable via env vars
declared in y.ENVIRONMENT_VARIABLES.

Example usage:
    from y._cache import get_lru_cache, get_ttl_cache

    # Get a cache with default maxsize
    cache = get_lru_cache()

    # Get a cache with block-specific maxsize
    block_cache = get_lru_cache("block")

    # Get a TTL cache
    ttl_cache = get_ttl_cache(ttl=300)
"""

from typing import Literal

import cachebox

from y import ENVIRONMENT_VARIABLES as ENVS

__all__ = [
    "get_lru_cache",
    "get_ttl_cache",
    "DEFAULT_LRU_CACHE",
    "BLOCK_LRU_CACHE",
    "CONTRACT_LRU_CACHE",
    "PRICE_LRU_CACHE",
]

CacheType = Literal["default", "block", "contract", "price"]


def get_lru_cache(cache_type: CacheType = "default") -> cachebox.LRUCache:
    """
    Get an LRU cache configured with the appropriate maxsize from environment variables.

    Args:
        cache_type: Type of cache determining which env var to use for maxsize.
            - "default": Uses DEFAULT_CACHE_MAXSIZE (default: 50,000)
            - "block": Uses BLOCK_CACHE_MAXSIZE (default: 500,000)
            - "contract": Uses CONTRACT_CACHE_MAXSIZE (default: 50,000)
            - "price": Uses PRICE_CACHE_MAXSIZE (default: 100,000)

    Returns:
        A new LRUCache instance with the configured maxsize.
    """
    maxsize_map = {
        "default": ENVS.DEFAULT_CACHE_MAXSIZE,
        "block": ENVS.BLOCK_CACHE_MAXSIZE,
        "contract": ENVS.CONTRACT_CACHE_MAXSIZE,
        "price": ENVS.PRICE_CACHE_MAXSIZE,
    }
    maxsize = maxsize_map[cache_type]
    return cachebox.LRUCache(maxsize)


def get_ttl_cache(cache_type: CacheType = "default", ttl: int | None = None) -> cachebox.TTLCache:
    """
    Get a TTL cache configured with the appropriate maxsize and TTL.

    Args:
        cache_type: Type of cache determining which env var to use for maxsize.
            Same options as get_lru_cache().
        ttl: Time-to-live in seconds. Defaults to ENVS.CACHE_TTL (1 hour).

    Returns:
        A new TTLCache instance with the configured maxsize and TTL.
    """
    if ttl is None:
        ttl = ENVS.CACHE_TTL
    maxsize_map = {
        "default": ENVS.DEFAULT_CACHE_MAXSIZE,
        "block": ENVS.BLOCK_CACHE_MAXSIZE,
        "contract": ENVS.CONTRACT_CACHE_MAXSIZE,
        "price": ENVS.PRICE_CACHE_MAXSIZE,
    }
    maxsize = maxsize_map[cache_type]
    return cachebox.TTLCache(maxsize, ttl=ttl)


# Pre-built default cache instances for convenience
DEFAULT_LRU_CACHE: cachebox.LRUCache = get_lru_cache("default")
BLOCK_LRU_CACHE: cachebox.LRUCache = get_lru_cache("block")
CONTRACT_LRU_CACHE: cachebox.LRUCache = get_lru_cache("contract")
PRICE_LRU_CACHE: cachebox.LRUCache = get_lru_cache("price")
