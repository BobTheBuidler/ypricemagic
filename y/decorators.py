
import functools
import os
from typing import Callable, TypeVar, Union
import asyncio

from typing_extensions import ParamSpec

DEBUG = os.environ.get('YPRICEMAGIC_DEBUG', False)

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
