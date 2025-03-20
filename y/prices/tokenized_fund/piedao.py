import logging
from decimal import Decimal
from typing import List, Optional

import a_sync
from a_sync import cgather
from brownie import ZERO_ADDRESS
from multicall import Call

from y import ENVIRONMENT_VARIABLES as ENVS
from y.classes.common import ERC20
from y.contracts import has_method
from y.datatypes import Address, AnyAddressType, Block, UsdPrice, UsdValue
from y.exceptions import call_reverted
from y.prices import magic
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)


@a_sync.a_sync(default="sync", cache_type="memory")
async def is_pie(token: AnyAddressType) -> bool:
    """
    Check if a given token is a PieDAO token.

    Args:
        token: The address of the token to check.

    Returns:
        True if the token is a PieDAO token, False otherwise.

    Example:
        >>> is_pie("0x1234567890abcdef1234567890abcdef12345678")
        True
    """
    return await has_method(token, "getCap()(uint)", sync=False)


@a_sync.a_sync(default="sync")
async def get_price(
    pie: AnyAddressType,
    block: Optional[Block] = None,
    skip_cache: bool = ENVS.SKIP_CACHE,
) -> UsdPrice:
    """
    Get the price of a PieDAO token in USD.

    Args:
        pie: The address of the PieDAO token.
        block: The block number to query the price at. Defaults to the latest block.
        skip_cache: Whether to skip the cache when fetching the price. Defaults to the value of ENVS.SKIP_CACHE.

    Example:
        >>> get_price("0x1234567890abcdef1234567890abcdef12345678")
        123.45

    See Also:
        - :func:`get_tvl`
        - :class:`ERC20`
    """
    tvl, total_supply = await cgather(
        get_tvl(pie, block, skip_cache=skip_cache),
        ERC20(pie, asynchronous=True).total_supply_readable(block),
    )
    return UsdPrice(tvl / total_supply)


async def get_tokens(
    pie_address: Address, block: Optional[Block] = None
) -> List[ERC20]:
    """
    Get the list of tokens in a PieDAO token.

    Args:
        pie_address: The address of the PieDAO token.
        block: The block number to query the tokens at. Defaults to the latest block.

    Returns:
        A list of :class:`ERC20` objects representing the tokens in the PieDAO token.

    Example:
        >>> get_tokens("0x1234567890abcdef1234567890abcdef12345678")
        [ERC20('0xTokenAddress1'), ERC20('0xTokenAddress2')]

    Note:
        This function retrieves token addresses using a multicall and then creates :class:`ERC20` instances from those addresses.
    """
    return [
        ERC20(t)
        for t in await Call(pie_address, "getTokens()(address[])", block_id=block)
    ]


async def get_bpool(pie_address: Address, block: Optional[Block] = None) -> Address:
    """
    Get the Balancer pool address for a PieDAO token.

    Args:
        pie_address: The address of the PieDAO token.
        block: The block number to query the pool at. Defaults to the latest block.

    Returns:
        The address of the Balancer pool, or the PieDAO address if no pool is found.

    Example:
        >>> get_bpool("0x1234567890abcdef1234567890abcdef12345678")
        '0xBpoolAddress'
    """
    try:
        bpool = await raw_call(
            pie_address, "getBPool()", output="address", block=block, sync=False
        )
        return bpool if bpool != ZERO_ADDRESS else pie_address
    except Exception as e:
        if not call_reverted(e):
            raise
        return pie_address


async def get_tvl(
    pie_address: Address,
    block: Optional[Block] = None,
    skip_cache: bool = ENVS.SKIP_CACHE,
) -> UsdValue:
    """
    Get the total value locked (TVL) in a PieDAO token in USD.

    Args:
        pie_address: The address of the PieDAO token.
        block: The block number to query the TVL at. Defaults to the latest block.
        skip_cache: Whether to skip the cache when fetching the TVL. Defaults to the value of ENVS.SKIP_CACHE.

    Example:
        >>> get_tvl("0x1234567890abcdef1234567890abcdef12345678")
        1000000.00

    See Also:
        - :func:`get_value`
        - :func:`get_bpool`
        - :func:`get_tokens`
    """
    tokens: List[ERC20]
    pool, tokens = await cgather(
        get_bpool(pie_address, block), get_tokens(pie_address, block)
    )
    return await a_sync.map(
        get_value, tokens, bpool=pool, block=block, skip_cache=skip_cache
    ).sum(pop=True, sync=False)


async def get_balance(
    bpool: Address, token: ERC20, block: Optional[Block] = None
) -> Decimal:
    """
    Get the balance of a token in a Balancer pool.

    Args:
        bpool: The address of the Balancer pool.
        token: The :class:`ERC20` token to query.
        block: The block number to query the balance at. Defaults to the latest block.

    Example:
        >>> get_balance("0xBpoolAddress", ERC20("0xTokenAddress"))
        1000.0
    """
    balance, scale = await cgather(
        Call(token.address, ("balanceOf(address)(uint)", bpool), block_id=block),
        token.__scale__,
    )
    return Decimal(balance) / scale


async def get_value(
    bpool: Address,
    token: ERC20,
    block: Optional[Block] = None,
    skip_cache: bool = ENVS.SKIP_CACHE,
) -> UsdValue:
    """
    Get the USD value of a token in a Balancer pool.

    Args:
        bpool: The address of the Balancer pool.
        token: The :class:`ERC20` token to query.
        block: The block number to query the value at. Defaults to the latest block.
        skip_cache: Whether to skip the cache when fetching the value. Defaults to the value of ENVS.SKIP_CACHE.

    Example:
        >>> get_value("0xBpoolAddress", ERC20("0xTokenAddress"))
        500.0

    Note:
        This function calculates the value by multiplying the token balance in the pool by its price.

    See Also:
        - :func:`get_balance`
    """
    balance, price = await cgather(
        get_balance(bpool, token, block),
        token.price(block, skip_cache=skip_cache, sync=False),
    )
    return UsdValue(balance * Decimal(price))
