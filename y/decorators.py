
import functools
import os
from typing import Any, Callable

DEBUG = os.environ.get('YPRICEMAGIC_DEBUG', False)

def continue_on_revert(func: Callable) -> Any:
    '''
    Decorates a call-making function. If the call reverts, returns `None`. Raises any other exceptions.
    '''
    from y.exceptions import continue_if_call_reverted

    @functools.wraps(func)
    def continue_on_revert_wrap(*args: Any, **kwargs: Any) -> Callable:
        try:
            return func(*args,**kwargs)
        except Exception as e:
            continue_if_call_reverted(e)
    
    return continue_on_revert_wrap
