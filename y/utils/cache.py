import functools
import os
from inspect import iscoroutinefunction
from logging import DEBUG, getLogger

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

    See Also:
        - :class:`joblib.Memory`
    """
    return Memory(f"cache/{chain.id}", verbose=0)


memory = _memory()

a_sync_ttl_cache: ASyncDecorator = a_sync.a_sync(ram_cache_ttl=ENVS.CACHE_TTL)


# NOTE: we have an optional disk cache that I made for debugging and decided to keep in for my own convenience.
# TODO: make a real disk cache

try:

    import toolcache

    """User has toolcache, this diskcache decorator will work."""

    logger = getLogger(__name__)
    cache_base_path = f"./cache/{chain.id}/"

    def optional_async_diskcache(fn: AnyFn[P, T]) -> AnyFn[P, T]:
        """
        Decorator to optionally apply disk caching to asynchronous functions.

        If the user has `toolcache` installed, this decorator will apply disk caching
        to the decorated asynchronous function. If `toolcache` is not installed, the
        function will be returned as is, without any caching applied.

        Args:
            fn: The function to be decorated. Must be asynchronous.

        Raises:
            NotImplementedError: If the function is synchronous.

        Examples:
            Using the decorator with an asynchronous function when `toolcache` is installed:

            >>> @optional_async_diskcache
            ... async def fetch_data():
            ...     return "data"

            This will cache the result of `fetch_data` in the specified cache directory.

            If `toolcache` is not installed, the function will run without caching:

            >>> async def fetch_data():
            ...     return "data"
            >>> fetch_data = optional_async_diskcache(fetch_data)

        See Also:
            - :mod:`toolcache`
        """
        if not iscoroutinefunction(fn):
            raise NotImplementedError(f"{fn} is sync")

        module = fn.__module__.replace(".", "/")
        cache_path_for_fn = cache_base_path + module + "/" + fn.__name__

        # Ensure the cache dir exists
        os.makedirs(cache_path_for_fn, exist_ok=True)

        if logger.isEnabledFor(DEBUG):

            @toolcache.cache("disk", cache_dir=cache_path_for_fn)
            @functools.wraps(fn)
            async def diskcache_wrap_with_debug_logs(*args, **kwargs) -> T:
                logger.debug(
                    "fetching %s(%s)", fn.__qualname__, ", ".join(map(str, args))
                )
                return await fn(*args, **kwargs)

            return diskcache_wrap_with_debug_logs

        else:

            @toolcache.cache("disk", cache_dir=cache_path_for_fn)
            @functools.wraps(fn)
            async def diskcache_wrap(*args, **kwargs) -> T:
                return await fn(*args, **kwargs)

            return diskcache_wrap

except ImportError:

    """User doesn't have toolcache, this decorator will just return the undecorated function."""

    def optional_async_diskcache(fn: AnyFn[P, T]) -> AnyFn[P, T]:
        """
        Decorator to optionally apply disk caching to asynchronous functions.

        If `toolcache` is not installed, this decorator will return the function
        as is, without any caching applied.

        Args:
            fn: The function to be decorated.

        Examples:
            Using the decorator with an asynchronous function:

            >>> async def fetch_data():
            ...     return "data"
            >>> fetch_data = optional_async_diskcache(fetch_data)

        See Also:
            - :mod:`toolcache`
        """
        return fn
