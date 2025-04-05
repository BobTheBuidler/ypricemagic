from asyncio import iscoroutinefunction
from functools import partial, wraps
from logging import getLogger
from typing import Callable, TypeVar, Union

from a_sync import debugging
from typing_extensions import ParamSpec


P = ParamSpec("P")
T = TypeVar("T")


stuck_coro_logger = getLogger("y.stuck?")
stuck_coro_debugger = partial(debugging.stuck_coro_debugger, logger=stuck_coro_logger)


def continue_on_revert(func: Callable[P, T]) -> Callable[P, T]:
    """
    Decorates a call-making function. If the call reverts, it attempts to continue
    by calling the standalone function :func:`continue_if_call_reverted` from the
    `y.exceptions` module. Raises any other exceptions.

    This decorator is useful for functions interacting with smart contracts where
    a call might revert due to various reasons. It ensures that the function does not
    fail completely on a revert, but instead handles it gracefully.

    Note:
        The decorated function will return `None` if the call reverts and
        :func:`continue_if_call_reverted` does not raise an exception.

    Args:
        func: The function to be decorated.

    Returns:
        The wrapped function with revert handling.

    Examples:
        >>> @continue_on_revert
        ... def fetch_data():
        ...     # some logic that might revert
        ...     pass

        >>> @continue_on_revert
        ... async def fetch_data_async():
        ...     # some async logic that might revert
        ...     pass

    See Also:
        - :func:`continue_if_call_reverted`
    """
    from y.exceptions import continue_if_call_reverted

    if iscoroutinefunction(func):

        @wraps(func)
        async def continue_on_revert_wrap(
            *args: P.args, **kwargs: P.kwargs
        ) -> Union[T, None]:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                continue_if_call_reverted(e)

    elif callable(func):

        @wraps(func)
        def continue_on_revert_wrap(
            *args: P.args, **kwargs: P.kwargs
        ) -> Union[T, None]:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                continue_if_call_reverted(e)

    else:
        raise NotImplementedError(f"Unable to decorate {func}")
    return continue_on_revert_wrap
