
import logging
import time
from functools import lru_cache, wraps
from typing import Callable, TypeVar
from typing_extensions import ParamSpec

from a_sync import a_sync
from pony.orm import (CommitException, OperationalError, TransactionError,
                      UnexpectedError, db_session)

from y._db.common import token_attr_threads

_T = TypeVar('_T')
_P = ParamSpec('_P')

logger = logging.getLogger(__name__)

def retry_locked(callable: Callable[_P, _T]) -> Callable[_P, _T]:
    @wraps(callable)
    def retry_locked_wrap(*args: _P.args, **kwargs: _P.kwargs) -> _T:
        sleep = 0.05
        while True:
            try:
                return callable(*args, **kwargs)
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

a_sync_db_session = lambda fn: a_sync(default='async', executor=token_attr_threads)(
    retry_locked(
        db_session(
            fn
        )
    )
)
a_sync_db_session_cached = lambda fn: a_sync(default='async', executor=token_attr_threads)(
    retry_locked(
        lru_cache(maxsize=None)(
            db_session(
                fn
            )
        )
    )
)