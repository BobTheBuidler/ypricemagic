
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

levels_down_the_rabbit_hole = defaultdict(lambda: defaultdict(int))

def log(logger: logging.Logger, key: str = "") -> Callable[[Callable[...,Any]],Callable[...,Any]]:
    """
    Decorates a function so both the inputs and outputs are logged with logger level `DEBUG`.
    """

    log_level = os.environ.get("LOG_LEVEL" if not key else f"LOG_LEVEL_{key}")
    if log_level:
        log_level = getattr(logging,log_level)

    def log_decorator(func: Callable[...,Any]) -> Callable[...,Any]:
        assert logger, 'To use @log decorator, you must pass in a logger.'

        @functools.wraps(func)
        def logging_wrap(*args: Any, **kwargs: Any) -> Any:
            start = time()
            pid, tid = os.getpid(), threading.get_ident()
            describer_string = f'{func.__name__}{tuple([*args])}'
            if kwargs:
                describer_string += f', kwargs: {[*kwargs.items()]}'
            if log_level:
                logger.setLevel(log_level)
            spacing = '  ' * levels_down_the_rabbit_hole[pid][tid]
            logger.debug(f'{spacing}Fetching {describer_string}')
            levels_down_the_rabbit_hole[pid][tid] += 1
            func_returns = func(*args,**kwargs)
            levels_down_the_rabbit_hole[pid][tid] -= 1
            logger.debug(f'{spacing}{describer_string} returns: {func_returns}')
            # record function duration for debug purposes
            if DEBUG:
                record_duration(func.__name__, describer_string, time() - start)
            return func_returns

        return logging_wrap

    return log_decorator
