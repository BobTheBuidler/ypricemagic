
import _thread
import asyncio
import functools
import logging
import os
from threading import Thread, main_thread
from typing import Any, Awaitable, Callable, NoReturn, TypeVar, Union

from typing_extensions import ParamSpec

DEBUG = os.environ.get('YPRICEMAGIC_DEBUG', False)

P = ParamSpec('P')
T = TypeVar('T')

def continue_on_revert(func: Callable[P, T]) -> Callable[P, T]:
    '''
    Decorates a call-making function. If the call reverts, returns `None`. Raises any other exceptions.
    '''
    from y.exceptions import continue_if_call_reverted

    @functools.wraps(func)
    def continue_on_revert_wrap(*args: P.args, **kwargs: P.kwargs) -> Union[T, None]:
        try:
            return func(*args,**kwargs)
        except Exception as e:
            continue_if_call_reverted(e)
    
    return continue_on_revert_wrap


async def _run_until_shutdown() -> None:
    """ Exits loop when main thread dies, killing worker thread. Runs in worker thread. """
    while main_thread().is_alive():
        await asyncio.sleep(5)

def _start_event_daemon(event_loop: asyncio.BaseEventLoop) -> None:
    asyncio.set_event_loop(event_loop)
    event_loop.run_until_complete(_run_until_shutdown())

@functools.lru_cache(maxsize=1)
def _event_daemon_event_loop() -> asyncio.BaseEventLoop:
    loop = asyncio.new_event_loop()
    thread = Thread(target=_start_event_daemon, args = (loop, ))
    thread.start()
    return loop

def event_daemon_task(func: Callable[P, Awaitable[Union[NoReturn, None]]]) -> Callable[P, Awaitable[None]]:
    """ Will submit coroutines to the event deamon thread's event loop. """
    if not asyncio.iscoroutinefunction(func):
        raise RuntimeError("You can only decorate coroutine functions with `run_in_event_daemon`.")
    @functools.wraps(func)
    async def daemon_wrap(*args: P.args, **kwargs: P.kwargs) -> None:
        #_event_daemon_event_loop().create_task(func(*args, **kwargs))
        asyncio.get_event_loop().create_task(func(*args, **kwargs))
    return daemon_wrap
