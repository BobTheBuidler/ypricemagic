
import logging
import os
from random import randrange
from sqlite3 import OperationalError
from time import sleep, time
from typing import Any, Callable

from requests.exceptions import HTTPError, ReadTimeout

from y.utils.debug import record_duration

retry_logger = logging.getLogger('auto_retry')
DEBUG = os.environ.get('YPRICEMAGIC_DEBUG', False)

def continue_on_revert(func: Callable) -> Any:
    '''
    Decorates a call-making function. If the call reverts, returns `None`. Raises any other exceptions.
    '''
    from y.exceptions import continue_if_call_reverted

    def continue_on_revert_wrap(*args: Any, **kwargs: Any) -> Callable:
        try:
            return func(*args,**kwargs)
        except Exception as e:
            continue_if_call_reverted(e)
    
    return continue_on_revert_wrap


def log(logger: logging.Logger):
    """
    Decorates a function so both the inputs and outputs are logged with logger level DEBUG.
    For convenience, also decorates the function with @auto_retry.
    """

    def log_decorator(func: Callable) -> Callable:
        assert logger, 'To use @debug_logging decorator, you must pass in a logger.'

        def logging_wrap(*args: Any, **kwargs: Any) -> Any:
            fn_name = func.__name__
            
            if DEBUG:
                start = time()

            if len(kwargs) == 0:
                describer_string = f'{fn_name}{tuple([*args])}'
            else:
                describer_string = f'{fn_name}{tuple([*args])}, kwargs: {[*kwargs.items()]}'
            
            logger.debug(f'Fetching {describer_string}')
            func_returns = retry_superwrap(*args,**kwargs)
            logger.debug(f'{describer_string} returns: {func_returns}')

            # record function duration for debug purposes
            if DEBUG:
                record_duration(fn_name, describer_string, time() - start)
                
            return func_returns
        
        @auto_retry
        def retry_superwrap(*args: Any, **kwargs: Any) -> Callable:
            return func(*args, **kwargs)

        return logging_wrap
    return log_decorator

def auto_retry(func):
    '''
    Decorator that will retry the function on:
    - ConnectionError
    - HTTPError
    - TimeoutError
    - ReadTimeout
    
    It will also retry on specific ValueError exceptions:
    - Max rate limit reached
    - please use API Key for higher rate limit
    - execution aborted (timeout = 5s)
    
    On repeat errors, will retry in increasing intervals.
    '''

    def retry_wrap(*args, **kwargs):
        i = 0
        sleep_time = randrange(10,20)
        while True:
            try:
                return func(*args, **kwargs)
            except ValueError as e:
                retry_on_errs = (
                    # Occurs on any chain when making computationally intensive calls. Just retry.
                    'execution aborted (timeout = 5s)',

                    # Usually from block explorer while fetching contract source code. Just retry.
                    'Max rate limit reached',
                    'please use API Key for higher rate limit',

                    # Occurs occasionally on AVAX when node is slow to sync. Just retry.
                    'after last accepted block',
                )
                if i > 10 or not any([err in str(e) for err in retry_on_errs]):
                    raise
                retry_logger.warning(f'{str(e)} [{i}]')
            except (ConnectionError, HTTPError, TimeoutError, ReadTimeout) as e:
                # This happens when we pass too large of a request to the node. Do not retry.
                if 'Too Large' in str(e) or '404' in str(e):
                    raise
                retry_logger.warning(f'{str(e)} [{i}]')
            except OperationalError as e:
                # This happens when brownie's deployments.db gets locked. Just retry.
                if 'database is locked' not in str(e):
                    raise
                retry_logger.warning(f'{str(e)} [{i}]')
            i += 1
            sleep(i * sleep_time)

    return retry_wrap
