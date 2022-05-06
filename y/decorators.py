
from collections import defaultdict
import functools
import logging
import os
import threading
from random import randrange
from sqlite3 import OperationalError
from time import sleep, time
from typing import Any, Callable, Tuple

from requests.exceptions import HTTPError, ReadTimeout

from y.utils.debug import record_duration
from y.utils.logging import yLazyLogger

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
