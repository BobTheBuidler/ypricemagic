"""
Utility functions for retrieving Ethereum client information.
"""

import logging

from async_lru import alru_cache
from brownie import web3
from cachetools.func import lru_cache
from dank_mids import dank_web3
from web3._utils.rpc_abi import RPC

from y.utils.logging import yLazyLogger

logger = logging.getLogger(__name__)


@lru_cache(1)
@yLazyLogger(logger)
def get_ethereum_client() -> str:
    """
    Get the Ethereum client type for the current connection.

    Returns:
        A string representing the Ethereum client type, such as 'geth', 'erigon', or 'tg'.

    Examples:
        >>> from y.utils.client import get_ethereum_client
        >>> client = get_ethereum_client()
        >>> print(client)
        'geth'

        >>> # Example with a different client
        >>> client = get_ethereum_client()
        >>> print(client)
        'erigon'

    See Also:
        - :func:`get_ethereum_client_async` for the asynchronous version of this function.
    """
    try:
        # web3py < 6.0
        version = web3.clientVersion
    except AttributeError:
        # web3py >= 6.0
        version = web3.client_version
    return _get_ethereum_client(version)


@alru_cache(maxsize=1)
async def get_ethereum_client_async() -> str:
    """
    Asynchronously get the Ethereum client type for the current connection.

    Returns:
        A string representing the Ethereum client type, such as 'geth', 'erigon', or 'tg'.

    Examples:
        >>> from y.utils.client import get_ethereum_client_async
        >>> client = await get_ethereum_client_async()
        >>> print(client)
        'erigon'

        >>> # Example with a different client
        >>> client = await get_ethereum_client_async()
        >>> print(client)
        'tg'

    See Also:
        - :func:`get_ethereum_client` for the synchronous version of this function.
    """
    return _get_ethereum_client(
        await dank_web3.manager.coro_request(RPC.web3_clientVersion, [])
    )


@yLazyLogger(logger)
def _get_ethereum_client(client: str) -> str:
    """
    Determine the Ethereum client type based on the client version string.

    Args:
        client: A string containing the client version information.

    Returns:
        A string representing the Ethereum client type, such as 'geth', 'erigon', or 'tg'.

    Examples:
        >>> from y.utils.client import _get_ethereum_client
        >>> client_type = _get_ethereum_client("Geth/v1.10.23-stable/linux-amd64/go1.18.7")
        >>> print(client_type)
        'geth'

        >>> # Example with a different client version
        >>> client_type = _get_ethereum_client("Erigon/v2021.07.2/linux-amd64/go1.16.5")
        >>> print(client_type)
        'erigon'
    """
    logger.debug("client: %s", client)
    return next(
        (
            identifier
            for prefix, identifier in _clients.items()
            if client.startswith(prefix)
        ),
        client,
    )


_clients = {
    "geth": "geth",
    "erigon": "erigon",
    "TurboGeth": "tg",
}
