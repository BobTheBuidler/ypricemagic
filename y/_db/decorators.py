
import logging
import time
from functools import lru_cache, wraps
from typing import Callable, Iterable, TypeVar
from typing_extensions import ParamSpec

import a_sync
from a_sync.a_sync import ASyncFunction
from brownie import chain
from pony.orm import (CommitException, OperationalError, TransactionError,
                      UnexpectedError, commit, db_session)

_T = TypeVar('_T')
_P = ParamSpec('_P')

logger = logging.getLogger(__name__)


ydb_read_threads = a_sync.PruningThreadPoolExecutor(16)
ydb_write_threads = a_sync.PruningThreadPoolExecutor(16)

def retry_locked(callable: Callable[_P, _T]) -> Callable[_P, _T]:
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
                logger.debug("%s.%s got exc %s", callable.__module__, callable.__name__, e)
                if "An attempt to mix objects belonging to different transactions" not in str(e):
                    raise
    return retry_locked_wrap

a_sync_read_db_session: Callable[[Callable[_P, _T]], ASyncFunction[_P, _T]] = lambda fn: a_sync.a_sync(default='async', executor=ydb_read_threads)(
    retry_locked(
        db_session(
            retry_locked(
                fn
            )
        )
    )
)

a_sync_write_db_session: Callable[[Callable[_P, _T]], ASyncFunction[_P, _T]] = lambda fn: a_sync.a_sync(default='async', executor=ydb_write_threads)(
    retry_locked(
        db_session(
            retry_locked(
                fn
            )
        )
    )
)

a_sync_write_db_session_cached: Callable[[Callable[_P, _T]], ASyncFunction[_P, _T]] = lambda fn: a_sync.a_sync(default='async', executor=ydb_write_threads, ram_cache_maxsize=None)(
    retry_locked(
        lru_cache(maxsize=None)(
            db_session(
                retry_locked(
                    fn
                )
            )
        )
    )
)


_result_count_logger = logging.getLogger(f"{__name__}.result_count")

def log_result_count(name: str, arg_names: Iterable[str] = []) -> Callable[[Callable[_P, _T]], Callable[_P, _T]]:
    def result_count_deco(fn: Callable[_P, _T]) -> Callable[_P, _T]:
        @wraps(fn)
        def result_count_wrap(*args: _P.args, **kwargs: _P.kwargs) -> _T:
            results = fn(*args, **kwargs)
            if _result_count_logger.isEnabledFor(logging.DEBUG):
                arg_values = ' '.join(f'{k} {v}' for k, v in [('chain', chain.id), *zip(arg_names, args)])
                _result_count_logger.debug("loaded %s %s for %s", len(results), name, arg_values)
            return results
        return result_count_wrap
    return result_count_deco
