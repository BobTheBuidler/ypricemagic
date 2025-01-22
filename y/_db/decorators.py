import logging
import time
from functools import lru_cache, wraps
from typing import Callable, Iterable, TypeVar
from typing_extensions import ParamSpec

from a_sync import PruningThreadPoolExecutor, a_sync
from a_sync.a_sync import ASyncFunction
from brownie import chain
from pony.orm import (
    CommitException,
    OperationalError,
    TransactionError,
    UnexpectedError,
    commit,
    db_session,
)


_T = TypeVar("_T")
_P = ParamSpec("_P")

logger = logging.getLogger(__name__)

ydb_read_threads = PruningThreadPoolExecutor(12)
ydb_write_threads = PruningThreadPoolExecutor(12)


def retry_locked(callable: Callable[_P, _T]) -> Callable[_P, _T]:
    """Retries a database operation if it encounters specific exceptions related to database locks.

    This decorator wraps a function and retries it with an increasing sleep interval if it encounters
    `CommitException`, `OperationalError`, or `UnexpectedError` with a "database is locked" message.
    It also handles `TransactionError` by checking for specific error messages related to transaction mixing.

    Args:
        callable: The function to be wrapped and retried.

    Returns:
        The wrapped function with retry logic.

    Examples:
        >>> @retry_locked
        ... def my_db_function():
        ...     # perform some database operations
        ...     pass

    See Also:
        - :func:`pony.orm.commit`
        - :func:`pony.orm.db_session`
    """

    @wraps(callable)
    def retry_locked_wrap(*args: _P.args, **kwargs: _P.kwargs) -> _T:
        sleep = 0.05
        while True:
            try:
                retval = callable(*args, **kwargs)
                commit()
                return retval
            except (CommitException, OperationalError, UnexpectedError) as e:
                log = logger.warning if sleep > 1 else logger.debug
                log("%s.%s got exc %s", callable.__module__, callable.__name__, e)
                if "database is locked" not in str(e):
                    raise
                time.sleep(sleep)
                sleep *= 1.5
            except TransactionError as e:
                logger.debug(
                    "%s.%s got exc %s", callable.__module__, callable.__name__, e
                )
                if (
                    "An attempt to mix objects belonging to different transactions"
                    not in str(e)
                ):
                    raise

    return retry_locked_wrap


db_session_retry_locked = lambda func: retry_locked(db_session(retry_locked(func)))

a_sync_read_db_session: Callable[[Callable[_P, _T]], ASyncFunction[_P, _T]] = (
    lambda fn: a_sync(default="async", executor=ydb_read_threads)(
        db_session_retry_locked(fn)
    )
)
"""Decorator for asynchronous read database sessions with retry logic.

This decorator wraps a function with an asynchronous database session for read operations,
applying retry logic for handling database locks.

Args:
    fn: The function to be wrapped.

Returns:
    An asynchronous function with read database session management and retry logic.

Examples:
    >>> @a_sync_read_db_session
    ... async def read_data():
    ...     # perform read operations
    ...     pass

See Also:
    - :func:`retry_locked`
    - :func:`pony.orm.db_session`
"""


db_session_cached = lambda func: retry_locked(
    lru_cache(maxsize=None)(db_session(retry_locked(func)))
)


_result_count_logger = logging.getLogger(f"{__name__}.result_count")
_CHAIN_INFO = "chain", chain.id


def log_result_count(
    name: str, arg_names: Iterable[str] = []
) -> Callable[[Callable[_P, _T]], Callable[_P, _T]]:
    """Logs the number of results returned by a function.

    This decorator logs the number of results returned by a function at the DEBUG level,
    including additional context such as the chain ID and argument values.

    Args:
        name: The name of the result being logged.
        arg_names: An iterable of argument names to include in the log.

    Returns:
        A decorator that logs the result count of the wrapped function.

    Examples:
        >>> @log_result_count("items", ["arg1", "arg2"])
        ... def get_items(arg1, arg2):
        ...     return [1, 2, 3]

    See Also:
        - :mod:`logging`
    """

    def result_count_deco(fn: Callable[_P, _T]) -> Callable[_P, _T]:
        @wraps(fn)
        def result_count_wrap(*args: _P.args, **kwargs: _P.kwargs) -> _T:
            results = fn(*args, **kwargs)
            if _result_count_logger.isEnabledFor(logging.DEBUG):
                arg_values = " ".join(
                    f"{k} {v}" for k, v in (_CHAIN_INFO, *zip(arg_names, args))
                )
                _result_count_logger.debug(
                    "loaded %s %s for %s", len(results), name, arg_values
                )
            return results

        return result_count_wrap

    return result_count_deco
