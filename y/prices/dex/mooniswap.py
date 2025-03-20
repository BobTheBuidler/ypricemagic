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

    Args:
        token: The address of the token to check.

    Returns:
        True if the token is a Mooniswap pool, False otherwise.

    Examples:
        >>> is_mooniswap_pool("0x1234567890abcdef1234567890abcdef12345678")
        True

        >>> is_mooniswap_pool("0xabcdefabcdefabcdefabcdefabcdefabcdef")
        False
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

    Args:
        token: The address of the pool token.
        block (optional): The block number to get the price at. Defaults to latest block.
        skip_cache (optional): Whether to skip the cache. Defaults to :obj:`ENVS.SKIP_CACHE`.

    Returns:
        The price of the pool token in USD as a :class:`~y.datatypes.UsdPrice`.

    Examples:
        >>> get_pool_price("0x1234567890abcdef1234567890abcdef12345678")
        UsdPrice('1.2345')

        >>> get_pool_price("0xabcdefabcdefabcdefabcdefabcdefabcdef", block=12345678)
        UsdPrice('0.9876')

    See Also:
        - :func:`y.prices.magic.get_price`
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
        bal0 /= 10**18
    elif token1 == ZERO_ADDRESS:
        bal1 /= 10**18

    totalVal = bal0 * float(price0) + bal1 * float(price1)
    price = totalVal / total_supply
    return Decimal(price)
