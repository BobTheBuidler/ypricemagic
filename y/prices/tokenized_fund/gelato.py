import logging
from typing import Optional

from a_sync import a_sync, cgather

import y.prices.magic
from y import ENVIRONMENT_VARIABLES as ENVS
from y import convert
from y.classes.common import ERC20
from y.contracts import has_methods
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.utils.cache import optional_async_diskcache
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)


@a_sync(default="sync", cache_type="memory", ram_cache_ttl=5 * 60)
@optional_async_diskcache
async def is_gelato_pool(token_address: AnyAddressType) -> bool:
    """
    Check if a given token address is a Gelato pool.

    Args:
        token_address: The address of the token to check.

    Returns:
        True if the token is a Gelato pool, False otherwise.

    Example:
        >>> is_gelato_pool("0x1234567890abcdef1234567890abcdef12345678")
        True

    See Also:
        - :func:`y.contracts.has_methods`
    """
    return await has_methods(
        token_address, ("gelatoBalance0()(uint)", "gelatoBalance1()(uint)"), sync=False
    )


@a_sync(default="sync")
async def get_price(
    token: AnyAddressType,
    block: Optional[Block] = None,
    skip_cache: bool = ENVS.SKIP_CACHE,
) -> UsdPrice:
    """
    Calculate the price of a Gelato pool token in USD.

    This function calculates the price of a Gelato pool token by retrieving the balances,
    scales, and prices of the pool's underlying assets (token0 and token1), calculating
    their total value, and dividing by the total supply of the pool token.

    Args:
        token: The address of the token to price.
        block: The block number at which to get the price. Defaults to None.
        skip_cache: Whether to skip the cache. Defaults to ENVS.SKIP_CACHE.

    Example:
        >>> get_price("0x1234567890abcdef1234567890abcdef12345678")
        123.45

    See Also:
        - :func:`y.prices.magic.get_price`
        - :class:`y.classes.common.ERC20`
    """
    address = await convert.to_address_async(token)

    token0, token1 = await cgather(
        raw_call(address, "token0()", block=block, output="address", sync=False),
        raw_call(address, "token1()", block=block, output="address", sync=False),
    )

    (
        balance0,
        balance1,
        scale0,
        scale1,
        price0,
        price1,
        total_supply,
    ) = await cgather(
        raw_call(address, "gelatoBalance0()", block=block, output="int", sync=False),
        raw_call(address, "gelatoBalance1()", block=block, output="int", sync=False),
        *map(ERC20._get_scale_for, (token0, token1)),
        y.prices.magic.get_price(token0, block, skip_cache=skip_cache, sync=False),
        y.prices.magic.get_price(token1, block, skip_cache=skip_cache, sync=False),
        ERC20(address, asynchronous=True).total_supply_readable(block, sync=False),
    )

    balance0 /= scale0
    balance1 /= scale1
    totalVal = balance0 * price0 + balance1 * price1
    return UsdPrice(totalVal / total_supply)
