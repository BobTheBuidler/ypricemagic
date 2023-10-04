
from functools import lru_cache


@lru_cache(maxsize=1)
def _get_get_block():
    try:
        from eth_portfolio._db.utils import get_block
    except ImportError:
        from y._db.utils import get_block
    return get_block
    
@lru_cache(maxsize=1)
def _get_get_token():
    try:
        from eth_portfolio._db.utils import get_block
    except ImportError:
        from y._db.utils import get_block
    return get_block
