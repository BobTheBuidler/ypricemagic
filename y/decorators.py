
from typing import Any, Callable

from y.exceptions import continue_if_call_reverted


def continue_on_revert(func: Callable) -> Any:
    '''
    Decorates a call-making function. If the call reverts, returns `None`. Raises any other exceptions.
    '''

    def wrap(*args, **kwargs):

        try: return func(*args,**kwargs)
        except Exception as e:
            continue_if_call_reverted(e)
    
    return wrap