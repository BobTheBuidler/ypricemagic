from typing import Optional

import a_sync
from async_lru import alru_cache
from brownie.convert.datatypes import EthAddress

from y import ENVIRONMENT_VARIABLES as ENVS
from y.classes.common import ERC20
from y.constants import CHAINID
from y.contracts import Contract
from y.datatypes import AnyAddressType
from y.networks import Network
from y.prices import magic
from y.exceptions import ContractNotVerified
from brownie.exceptions import ContractNotFound


@a_sync.a_sync(default="sync")
async def is_solidex_deposit(token: AnyAddressType) -> bool:
    """
    Determine if a given token is a Solidex deposit token.

    This function checks if the current network is Fantom and if the token contract
    has a `pool` attribute. It also verifies that the token name starts with "Solidex"
    and ends with "Deposit".

    Args:
        token: The address of the token to check.

    Returns:
        True if the token is a Solidex deposit token, False otherwise.

    Examples:
        >>> await is_solidex_deposit("0xTokenAddress")
        True

    See Also:
        - :func:`y.contracts.Contract`
        - :class:`y.classes.common.ERC20`
    """
    if CHAINID != Network.Fantom:
        return False
    try:
        contract = await Contract.coroutine(token)
    except (ContractNotVerified, ContractNotFound):
        return False
    if not hasattr(contract, "pool"):
        return False
    name = await ERC20(token, asynchronous=True).name
    return name.startswith("Solidex") and name.endswith("Deposit")


@a_sync.a_sync(default="sync")
async def get_price(
    token: AnyAddressType,
    block: Optional[int] = None,
    skip_cache: bool = ENVS.SKIP_CACHE,
):
    """
    Retrieve the price of a given token.

    This function first obtains the associated pool using the cached :func:`_get_pool` function
    and then calls :func:`magic.get_price` on that pool to retrieve the price.

    Args:
        token: The address of the token to get the price for.
        block: The block number to query. Defaults to the latest block.
        skip_cache: If True, skip using the cache while fetching price data.

    Examples:
        >>> await get_price("0xTokenAddress")
        123.45

    See Also:
        - :func:`_get_pool`
        - :func:`y.prices.magic.get_price`
    """
    pool = await _get_pool(str(token))  # force to string for cache key
    return await magic.get_price(pool, block, skip_cache=skip_cache, sync=False)


@alru_cache(maxsize=None)
async def _get_pool(token) -> EthAddress:
    """
    Retrieve the pool address from a token contract.

    This function calls the `pool` method on the token contract to get the associated
    pool address. The result is cached to improve performance on subsequent calls.

    Args:
        token: The address of the token to get the pool for.

    Examples:
        >>> await _get_pool("0xTokenAddress")
        '0xPoolAddress'

    See Also:
        - :func:`y.contracts.Contract`
    """
    contract = await Contract.coroutine(token)
    return await contract.pool
