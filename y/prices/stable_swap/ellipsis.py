import logging
from decimal import Decimal
from typing import List, Optional

import a_sync
from a_sync import cgather

from y import ENVIRONMENT_VARIABLES as ENVS
from y.classes.common import ERC20, WeiBalance
from y.contracts import Contract, has_methods
from y.datatypes import AddressOrContract, AnyAddressType, Block, UsdPrice
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)


@a_sync.a_sync(default="sync", cache_type="memory", ram_cache_ttl=5 * 60)
async def is_eps_rewards_pool(token_address: AnyAddressType) -> bool:
    """
    Check if a given token address is an EPS rewards pool.

    This function verifies if the specified token address has the methods
    associated with an EPS rewards pool.

    Args:
        token_address: The address of the token to check.

    Returns:
        True if the token address is an EPS rewards pool, False otherwise.

    Examples:
        >>> await is_eps_rewards_pool("0x1234567890abcdef1234567890abcdef12345678")
        True

    See Also:
        - :func:`y.contracts.has_methods`
    """
    return await has_methods(
        token_address,
        (
            "lpStaker()(address)",
            "rewardTokens(uint)(address)",
            "rewardPerToken(address)(uint)",
            "minter()(address)",
        ),
        sync=False,
    )


@a_sync.a_sync(default="sync")
async def get_price(
    token_address: AddressOrContract,
    block: Optional[Block] = None,
    skip_cache: bool = ENVS.SKIP_CACHE,
) -> UsdPrice:
    """
    Get the USD price of a token at a specific block.

    This function calculates the price of a token in USD by determining the
    total value locked (TVL) and dividing it by the total supply of the token.

    Args:
        token_address: The address of the token to get the price for.
        block: The block number to query. Defaults to the latest block.
        skip_cache: If True, skip using the cache while fetching price data.

    Returns:
        The price of the token in USD.

    Examples:
        >>> await get_price("0x1234567890abcdef1234567890abcdef12345678")
        UsdPrice(1.23)

    See Also:
        - :class:`y.classes.common.ERC20`
        - :class:`y.classes.common.WeiBalance`
        - :func:`y.utils.raw_calls.raw_call`
    """
    minter = await raw_call(
        token_address, "minter()", output="address", block=block, sync=False
    )
    minter = await Contract.coroutine(minter)
    balances: List[WeiBalance]
    i, balances = 0, []
    while True:
        try:
            coin, balance = await cgather(
                minter.coins.coroutine(i, block_identifier=block),
                minter.balances.coroutine(i, block_identifier=block),
            )
            balance /= await ERC20._get_scale_for(coin)
            balances.append(WeiBalance(balance, coin, block, skip_cache=skip_cache))
            i += 1
        except:
            break
    tvl, total_supply = await cgather(
        WeiBalance.value_usd.sum(balances, sync=False),
        ERC20(token_address, asynchronous=True).total_supply_readable(block),
    )
    return UsdPrice(tvl / Decimal(total_supply))
