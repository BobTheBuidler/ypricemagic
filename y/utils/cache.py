
import functools
import logging
import os
from inspect import iscoroutinefunction

import a_sync
import eth_retry

from a_sync._typing import AnyFn, P, T
from a_sync.a_sync.function import ASyncDecorator
from brownie import chain
from joblib import Memory

from y import ENVIRONMENT_VARIABLES as ENVS


@eth_retry.auto_retry
def _memory():
    """
    Create and return a :class:`Memory` object for caching values for the currently connected blockchain.

    Returns:
        A :class:`~Memory` object configured with the current chain's cache directory.
    """
    return Memory(f"cache/{chain.id}", verbose=0)

memory = _memory()

a_sync_ttl_cache: ASyncDecorator = a_sync.a_sync(ram_cache_ttl=ENVS.CACHE_TTL)


# NOTE: we have an optional disk cache that I made for debugging and decided to keep in for my own convenience.
# TODO: make a real disk cache

try:

    import toolcache

    """User doesn't has toolcache, this diskcache decorator will work."""

    logger = logging.getLogger(__name__)
    cache_base_path = f'./cache/{chain.id}/'

    def optional_async_diskcache(fn: AnyFn[P, T]) -> AnyFn[P, T]:
        if not iscoroutinefunction(fn):
            raise NotImplementedError(f'{fn} is sync')
        
        module = fn.__module__.replace('.','/')
        cache_path_for_fn = cache_base_path + module + '/' + fn.__name__

        # Ensure the cache dir exists
        os.makedirs(cache_path_for_fn, exist_ok=True)

        @toolcache.cache('disk', cache_dir=cache_path_for_fn)
        @functools.wraps(fn)
        async def diskcache_wrap(*args, **kwargs) -> T:
            logger.debug(f"fetching {fn.__qualname__}({', '.join(str(a) for a in args)})")
            return await fn(*args, **kwargs)
        return diskcache_wrap
        
except ImportError:

    """User doesn't have toolcache, this decorator will just return the undecorated function."""

    def optional_async_diskcache(fn: AnyFn[P, T]) -> AnyFn[P, T]:
        return fn