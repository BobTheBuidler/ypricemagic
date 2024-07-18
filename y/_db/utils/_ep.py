
from functools import lru_cache

from y._db.utils.utils import ensure_chain

"""
if installed, eth_portfolio extends the db with some extra stuffs and we want to insert the objects to the db using the extended classes.
The functions in this file lets us do that.
"""

@lru_cache(maxsize=1)
def _get_get_block():
    ensure_chain()
    try:
        from eth_portfolio._db.utils import get_block
    except ModuleNotFoundError:
        from y._db.utils import get_block
    return get_block
    
@lru_cache(maxsize=1)
def _get_get_token():
    ensure_chain()
    try:
        from eth_portfolio._db.utils import get_token
    except ModuleNotFoundError:
        from y._db.utils.token import get_token
    # force imports to run in main thread
    import y._db.utils.token
    return get_token
