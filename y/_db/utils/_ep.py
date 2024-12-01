from functools import lru_cache

from y._db.utils.utils import ensure_chain

"""
This module provides utility functions to retrieve the `get_block` and `get_token` 
functions from either the `eth_portfolio` or `ypricemagic` database utilities, 
depending on the availability of the `eth_portfolio` module.

These functions are used to ensure that the correct version of the database 
utilities is used, allowing for extended functionality if `eth_portfolio` is installed.
"""


@lru_cache(maxsize=1)
def _get_get_block():
    """Retrieve the `get_block` function from the appropriate module.

    This function first ensures that the chain object for the connected chain
    has been inserted into the database. It then attempts to import the
    `get_block` function from `eth_portfolio._db.utils` if the `eth_portfolio`
    module is installed. If the module is not installed, it falls back to
    importing `get_block` from `y._db.utils`.

    Examples:
        >>> get_block = _get_get_block()
        >>> block = get_block(12345678)
        >>> print(block)

    See Also:
        - :func:`y._db.utils.utils.ensure_chain`
        - :func:`y._db.utils.utils.get_block`
    """
    ensure_chain()
    try:
        from eth_portfolio._db.utils import get_block
    except ModuleNotFoundError:
        from y._db.utils import get_block
    return get_block


@lru_cache(maxsize=1)
def _get_get_token():
    """Retrieve the `get_token` function from the appropriate module.

    This function first ensures that the chain object for the connected chain
    has been inserted into the database. It then attempts to import the
    `get_token` function from `eth_portfolio._db.utils` if the `eth_portfolio`
    module is installed. If the module is not installed, it falls back to
    importing `get_token` from `y._db.utils.token`.

    Additionally, it forces imports to run in the main thread to ensure
    compatibility.

    Examples:
        >>> get_token = _get_get_token()
        >>> token = get_token("0x1234567890abcdef1234567890abcdef12345678")
        >>> print(token)

    See Also:
        - :func:`y._db.utils.utils.ensure_chain`
        - :func:`y._db.utils.token.get_token`
    """
    ensure_chain()
    try:
        from eth_portfolio._db.utils import get_token
    except ModuleNotFoundError:
        from y._db.utils.token import get_token
    # force imports to run in main thread
    import y._db.utils.token

    return get_token
