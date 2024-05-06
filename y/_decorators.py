
import asyncio
import functools
import inspect
import logging
import time
from typing import AsyncIterator, Awaitable, Callable, NoReturn, TypeVar, Union, overload

from a_sync import ASyncGenericBase
from a_sync.a_sync.method import ASyncBoundMethod
from a_sync.iter import ASyncGeneratorFunction
from typing_extensions import Concatenate, ParamSpec

P = ParamSpec('P')
T = TypeVar('T')

def continue_on_revert(func: Callable[P, T]) -> Callable[P, T]:
    '''
    Decorates a call-making function. If the call reverts, returns `None`. Raises any other exceptions.
    '''
    from y.exceptions import continue_if_call_reverted

    if asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def continue_on_revert_wrap(*args: P.args, **kwargs: P.kwargs) -> Union[T, None]:
            try:
                return await func(*args,**kwargs)
            except Exception as e:
                continue_if_call_reverted(e)
    elif callable(func):
        @functools.wraps(func)
        def continue_on_revert_wrap(*args: P.args, **kwargs: P.kwargs) -> Union[T, None]:
            try:
                return func(*args,**kwargs)
            except Exception as e:
                continue_if_call_reverted(e)
    else:
        raise NotImplementedError(f"Unable to decorate {func}")
    return continue_on_revert_wrap

B = TypeVar("B", bound=ASyncGenericBase)

@overload
def stuck_coro_debugger(fn: Callable[Concatenate[B, P], AsyncIterator[T]]) -> ASyncGeneratorFunction[P, T]:...
@overload
def stuck_coro_debugger(fn: Callable[Concatenate[B, P], Awaitable[T]]) -> ASyncBoundMethod[B, P, T]:...
@overload
def stuck_coro_debugger(fn: Callable[Concatenate[B, P], T]) -> ASyncBoundMethod[B, P, T]:...
@overload
def stuck_coro_debugger(fn: Callable[P, AsyncIterator[T]]) -> Callable[P, AsyncIterator[T]]:...
@overload
def stuck_coro_debugger(fn: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:...
def stuck_coro_debugger(fn):
    logger = logging.getLogger("y.stuck?")
    if inspect.isasyncgenfunction(fn):
        @functools.wraps(fn)
        async def stuck_async_gen_wrap(*args: P.args, **kwargs: P.kwargs) -> AsyncIterator[T]:
            if not logger.isEnabledFor(logging.DEBUG):
                async for thing in fn(*args, **kwargs):
                    yield thing
            t = asyncio.create_task(coro=_stuck_debug_task(logger, fn, args, kwargs), name="_stuck_debug_task")
            try:
                async for thing in fn(*args, **kwargs):
                    yield thing
                t.cancel()
                return
            except Exception as e:
                t.cancel()
                raise
        return stuck_async_gen_wrap
    else:
        @functools.wraps(fn)
        async def stuck_coro_wrap(*args: P.args, **kwargs: P.kwargs) -> T:
            if not logger.isEnabledFor(logging.DEBUG):
                return await fn(*args, **kwargs)
            t = asyncio.create_task(coro=_stuck_debug_task(logger, fn, args, kwargs), name="_stuck_debug_task")
            try:
                retval = await fn(*args, **kwargs)
                t.cancel()
            except Exception as e:
                t.cancel()
                raise
            return retval
        return stuck_coro_wrap

async def _stuck_debug_task(logger: logging.Logger, fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> NoReturn:
    start = time.time()
    while True:
        await asyncio.sleep(300)
        logger._log(
            logging.DEBUG, 
            f"{fn.__module__}.{fn.__name__} still executing after {round((time.time() - start)/60, 2)}m with"
            + f" args {tuple(str(arg) for arg in args)}"
            + f" kwargs {dict((k, str(v)) for k, v in kwargs.items())}",
            (),
        )