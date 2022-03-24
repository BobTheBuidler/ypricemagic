
from typing import Any, Callable


def continue_on_revert(func: Callable) -> Any:
    '''
    Decorates a call-making function. If the call reverts, returns `None`. Raises any other exceptions.
    '''
    from y.exceptions import continue_if_call_reverted

    def retry_wrap(*args: Any, **kwargs: Any):

        try:
            return func(*args,**kwargs)
        except Exception as e:
            continue_if_call_reverted(e)
    
    return retry_wrap


def log(logger):

    def log_decorator(func):
        assert logger, 'To use @debug_logging decorator, you must pass in a logger.'

        def logging_wrap(*args: Any, **kwargs: Any):
            fn_name = func.__name__

            if len(kwargs) == 0:
                describer_string = f'{fn_name}{tuple([*args])}'
            else:
                describer_string = f'{fn_name}{tuple([*args])}, kwargs: {[*kwargs.items()]}'
            
            logger.debug(f'Fetching {describer_string}')
            func_returns = func(*args,**kwargs)
            logger.debug(f'{describer_string} returns: {func_returns}')
            return func_returns

        return logging_wrap
    return log_decorator
