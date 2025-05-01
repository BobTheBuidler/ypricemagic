import logging
from decimal import Decimal
from typing import Optional

import dank_mids
from a_sync import a_sync, cgather
from brownie import ZERO_ADDRESS, chain

from y import ENVIRONMENT_VARIABLES as ENVS
from y import convert
from y.classes.common import ERC20
from y.constants import weth
from y.contracts import Contract
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.prices import magic
from y.utils import gather_methods

logger = logging.getLogger(__name__)

if chain.id == 1:
    router = Contract("0xbAF9A5d4b0052359326A6CDAb54BABAa3a3A9643")
    gas_coin = weth
elif chain.id == 56:
    router = Contract("0xD41B24bbA51fAc0E4827b6F94C0D6DDeB183cD64")
    gas_coin = Contract("0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c")  # wbnb
else:
    router = None
    gas_coin = None


@a_sync(default="sync", ram_cache_ttl=5 * 60)
async def is_mooniswap_pool(token: AnyAddressType) -> bool:
    """
    Check if the given token address is a Mooniswap pool.

    This function converts the token address and uses the router contract's
    `isPool` method to determine if the token is a Mooniswap pool. Note that
    if the active chain does not configure the Mooniswap router (i.e. chain IDs
    other than 1 and 56), the function always returns False.

    Args:
        token: The address of the token to check.

    Returns:
        True if the token is a Mooniswap pool and the router is configured; otherwise, False.

    Examples:
        >>> is_mooniswap_pool("0x1234567890abcdef1234567890abcdef12345678")
        True
        >>> is_mooniswap_pool("0xabcdefabcdefabcdefabcdefabcdefabcdef")
        False

    See Also:
        :func:`~y.prices.magic.get_price`
    """
    address = await convert.to_address_async(token)
    return False if router is None else await router.isPool.coroutine(address)


@a_sync(default="sync")
async def get_pool_price(
    token: AnyAddressType,
    block: Optional[Block] = None,
    skip_cache: bool = ENVS.SKIP_CACHE,
) -> UsdPrice:
    """
    Get the price of the given Mooniswap pool token.

    This function retrieves the underlying token addresses with the pool's
    `token0` and `token1` methods, and then obtains the corresponding token balances
    and USD prices via asynchronous calls. It computes the total USD value of the pool
    by multiplying each token balance with its USD price, sums these values, and divides
    by the total supply of pool tokens. Although the return type is declared as
    UsdPrice, the function returns a Decimal value.

    Args:
        token: The address of the pool token.
        block: The block number at which to retrieve the data. Defaults to the latest block.
        skip_cache: Whether to skip using the cache for price retrieval. Defaults to :obj:`ENVS.SKIP_CACHE`.

    Returns:
        The computed USD price of the pool token as a Decimal. Note that this differs from the
        documented UsdPrice type.

    Examples:
        >>> price = get_pool_price("0x1234567890abcdef1234567890abcdef12345678")
        >>> print(price)
        1.2345
        >>> price = get_pool_price("0xabcdefabcdefabcdefabcdefabcdefabcdef", block=12345678)
        >>> print(price)
        0.9876

    See Also:
        :func:`~y.prices.magic.get_price`
    """
    address = await convert.to_address_async(token)
    token0, token1 = await gather_methods(address, ("token0", "token1"))
    bal0, bal1, price0, price1, total_supply = await cgather(
        (
            dank_mids.eth.get_balance(address, block_identifier=block)
            if token0 == ZERO_ADDRESS
            else ERC20(token0, asynchronous=True).balance_of_readable(address, block)
        ),
        (
            dank_mids.eth.get_balance(address, block_identifier=block)
            if token1 == ZERO_ADDRESS
            else ERC20(token1, asynchronous=True).balance_of_readable(address, block)
        ),
        (
            magic.get_price(gas_coin, block, skip_cache=skip_cache, sync=False)
            if token0 == ZERO_ADDRESS
            else magic.get_price(token0, block, skip_cache=skip_cache, sync=False)
        ),
        (
            magic.get_price(gas_coin, block, skip_cache=skip_cache, sync=False)
            if token1 == ZERO_ADDRESS
            else magic.get_price(token1, block, skip_cache=skip_cache, sync=False)
        ),
        ERC20(address, asynchronous=True).total_supply_readable(block),
    )

    if token0 == ZERO_ADDRESS:
        bal0 = Decimal(bal0) / 10**18
    elif token1 == ZERO_ADDRESS:
        bal1 = Decimal(bal1) / 10**18

    totalVal = bal0 * Decimal(price0) + bal1 * Decimal(price1)
    return totalVal / Decimal(total_supply)
