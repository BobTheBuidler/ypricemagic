
from functools import lru_cache

"""
if installed, eth_portfolio extends the db with some extra stuffs and we want to insert the objects to the db using the extended classes.
The functions in this file lets us do that.
"""

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
        from eth_portfolio._db.utils import get_token
    except ImportError:
        from y._db.utils import get_token
    return get_token
