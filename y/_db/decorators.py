
import logging
import time
from functools import lru_cache, wraps
from typing import Callable, TypeVar
from typing_extensions import ParamSpec

import a_sync
from pony.orm import (CommitException, OperationalError, TransactionError,
                      UnexpectedError, commit, db_session)

_T = TypeVar('_T')
_P = ParamSpec('_P')

logger = logging.getLogger(__name__)


ydb_read_threads = a_sync.PruningThreadPoolExecutor(32)
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
                logger.debug("%s.%s got exc %s", callable.__module__, callable.__name__, e)
                if "database is locked" not in str(e):
                    raise e
                time.sleep(sleep)
                sleep *= 1.5
            except TransactionError as e:
                logger.debug("%s.%s got exc %s", callable.__module__, callable.__name__, e)
                if "An attempt to mix objects belonging to different transactions" not in str(e):
                    raise e
    return retry_locked_wrap

a_sync_read_db_session = lambda fn: a_sync.a_sync(default='async', executor=ydb_write_threads)(
    db_session(
        retry_locked(
            fn
        )
    )
)

a_sync_write_db_session = lambda fn: a_sync.a_sync(default='async', executor=ydb_read_threads)(
    db_session(
        retry_locked(
            fn
        )
    )
)

a_sync_read_db_session_cached = lambda fn: a_sync.a_sync(default='async', executor=ydb_read_threads)(
    retry_locked(
        lru_cache(maxsize=None)(
            db_session(
                fn
            )
        )
    )
)

a_sync_write_db_session_cached = lambda fn: a_sync.a_sync(default='async', executor=ydb_read_threads)(
    retry_locked(
        lru_cache(maxsize=None)(
            db_session(
                fn
            )
        )
    )
)
