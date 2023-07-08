
import asyncio
import functools
import logging
import time
from typing import Awaitable, Callable, TypeVar, Union

from typing_extensions import ParamSpec

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

def stuck_coro_debugger(fn: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    logger = logging.getLogger("y.stuck?")
    @functools.wraps(fn)
    async def stuck_coro_wrap(*args: P.args, **kwargs: P.kwargs) -> T:
        if not logger.isEnabledFor(logging.DEBUG):
            return await fn(*args, **kwargs)
        t = asyncio.create_task(_stuck_debug_task(logger, fn, args, kwargs))
        retval = await fn(*args, **kwargs)
        t.cancel()
        return retval
    return stuck_coro_wrap

async def _stuck_debug_task(logger: logging.Logger, fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs):
    start = time.time()
    while True:
        await asyncio.sleep(300)
        logger._log(
            logging.DEBUG, 
            f"{fn.__module__}.{fn.__name__} still executing after {round(time.time() - start, 2)}s with"
            + f" args {tuple(str(arg) for arg in args)}"
            + f" kwargs {dict((k, str(v)) for k, v in kwargs.items())}",
            (),
        )