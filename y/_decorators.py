from asyncio import create_task, iscoroutinefunction, sleep
from functools import wraps
from inspect import isasyncgenfunction
from logging import DEBUG, Logger, getLogger
from time import time
from typing import (
    AsyncIterator,
    Awaitable,
    Callable,
    NoReturn,
    TypeVar,
    Union,
    overload,
)

from a_sync import ASyncGenericBase
from a_sync.a_sync.method import ASyncBoundMethod
from a_sync.iter import ASyncGeneratorFunction
from typing_extensions import Concatenate, ParamSpec

P = ParamSpec("P")
T = TypeVar("T")


def continue_on_revert(func: Callable[P, T]) -> Callable[P, T]:
    """
    Decorates a call-making function. If the call reverts, it attempts to continue
    by calling the standalone function :func:`continue_if_call_reverted` from the
    `y.exceptions` module. Raises any other exceptions.

    This decorator is useful for functions interacting with smart contracts where
    a call might revert due to various reasons. It ensures that the function does not
    fail completely on a revert, but instead handles it gracefully.

    Note:
        The decorated function will return `None` if the call reverts and
        :func:`continue_if_call_reverted` does not raise an exception.

    Args:
        func: The function to be decorated.

    Returns:
        The wrapped function with revert handling.

    Examples:
        >>> @continue_on_revert
        ... def fetch_data():
        ...     # some logic that might revert
        ...     pass

        >>> @continue_on_revert
        ... async def fetch_data_async():
        ...     # some async logic that might revert
        ...     pass

    See Also:
        - :func:`continue_if_call_reverted`
    """
    from y.exceptions import continue_if_call_reverted

    if iscoroutinefunction(func):

        @wraps(func)
        async def continue_on_revert_wrap(
            *args: P.args, **kwargs: P.kwargs
        ) -> Union[T, None]:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                continue_if_call_reverted(e)

    elif callable(func):

        @wraps(func)
        def continue_on_revert_wrap(
            *args: P.args, **kwargs: P.kwargs
        ) -> Union[T, None]:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                continue_if_call_reverted(e)

    else:
        raise NotImplementedError(f"Unable to decorate {func}")
    return continue_on_revert_wrap


B = TypeVar("B", bound=ASyncGenericBase)


stuck_coro_logger = getLogger("y.stuck?")
__stuck_coro_logger_is_enabled_for = stuck_coro_logger.isEnabledFor
__stuck_coro_logger_log = stuck_coro_logger._log


@overload
def stuck_coro_debugger(
    fn: Callable[Concatenate[B, P], AsyncIterator[T]],
) -> ASyncGeneratorFunction[P, T]: ...


@overload
def stuck_coro_debugger(
    fn: Callable[Concatenate[B, P], Awaitable[T]],
) -> ASyncBoundMethod[B, P, T]: ...


@overload
def stuck_coro_debugger(
    fn: Callable[Concatenate[B, P], T],
) -> ASyncBoundMethod[B, P, T]: ...


@overload
def stuck_coro_debugger(
    fn: Callable[P, AsyncIterator[T]],
) -> Callable[P, AsyncIterator[T]]: ...


@overload
def stuck_coro_debugger(fn: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]: ...


def stuck_coro_debugger(fn):
    if isasyncgenfunction(fn):

        @wraps(fn)
        async def stuck_async_gen_wrap(
            *args: P.args, **kwargs: P.kwargs
        ) -> AsyncIterator[T]:
            aiterator = fn(*args, **kwargs)

            if not __stuck_coro_logger_is_enabled_for(DEBUG):
                async for thing in aiterator:
                    yield thing
                return

            task = create_task(
                coro=_stuck_debug_task(fn, args, kwargs),
                name="_stuck_debug_task",
            )
            try:
                async for thing in aiterator:
                    yield thing
            finally:
                task.cancel()

        return stuck_async_gen_wrap
    else:

        @wraps(fn)
        async def stuck_coro_wrap(*args: P.args, **kwargs: P.kwargs) -> T:
            if not __stuck_coro_logger_is_enabled_for(DEBUG):
                return await fn(*args, **kwargs)

            task = create_task(
                coro=_stuck_debug_task(fn, args, kwargs),
                name="_stuck_debug_task",
            )
            try:
                retval = await fn(*args, **kwargs)
            finally:
                task.cancel()
            return retval

        return stuck_coro_wrap


async def _stuck_debug_task(
    fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs
) -> NoReturn:
    # sleep early so fast-running coros can exit early
    await sleep(300)

    start = time() - 300
    module = fn.__module__
    name = fn.__name__
    formatted_args = tuple(str(arg) for arg in args)
    formatted_kwargs = dict((k, str(v)) for k, v in kwargs.items())
    while True:
        __stuck_coro_logger_log(
            DEBUG,
            "%s.%s still executing after %sm with args %s kwargs %s",
            (
                module,
                name,
                round((time() - start) / 60, 2),
                formatted_args,
                formatted_kwargs,
            ),
        )
        await sleep(300)
