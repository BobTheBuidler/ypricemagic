import logging
from typing import Optional, Tuple

import a_sync

from y import ENVIRONMENT_VARIABLES as ENVS
from y import convert
from y.classes.common import ERC20, WeiBalance
from y.contracts import has_methods
from y.datatypes import AnyAddressType, Block, UsdPrice, UsdValue
from y.exceptions import call_reverted
from y.utils import gather_methods
from y.utils.cache import optional_async_diskcache

_RESERVES_METHODS = (
    "token0()(address)",
    "token1()(address)",
    "usersAmounts()((uint,uint))",
)

logger = logging.getLogger(__name__)


@a_sync.a_sync(default="sync", cache_type="memory", ram_cache_ttl=5 * 60)
@optional_async_diskcache
async def is_popsicle_lp(token_address: AnyAddressType) -> bool:
    """
    Determines if the given token address is a Popsicle Finance LP token.

    Args:
        token_address: The address of the token to check.

    Returns:
        True if the token is a Popsicle LP token, False otherwise.

    Example:
        >>> is_popsicle = is_popsicle_lp("0xd2C5A739ebfE3E00CFa88A51749d367d7c496CCf")
        >>> print(is_popsicle)
        True
    """
    # NOTE: contract to check for reference (mainnet): 0xd2C5A739ebfE3E00CFa88A51749d367d7c496CCf
    return await has_methods(
        token_address,
        ("token0()(address)", "token1()(address)", "usersAmounts()((uint,uint))"),
        sync=False,
    )


@a_sync.a_sync(default="sync")
async def get_price(
    token: AnyAddressType,
    block: Optional[Block] = None,
    *,
    skip_cache: bool = ENVS.SKIP_CACHE
) -> Optional[UsdPrice]:
    """
    Calculates the price of a Popsicle Finance LP token.

    Args:
        token: The address of the Popsicle LP token.
        block (optional): The block number to query. Defaults to the latest block.
        skip_cache (optional): Whether to skip the cache when fetching prices. Defaults to :obj:`ENVS.SKIP_CACHE`.

    Returns:
        The price of the LP token in USD, or None if the price cannot be determined.

    Example:
        >>> price = get_price("0xd2C5A739ebfE3E00CFa88A51749d367d7c496CCf", block=14_000_000)
        >>> print(f"{price:.6f}")
        1.234567  # The price of the Popsicle LP token in USD

    See Also:
        - :func:`get_tvl`
        - :func:`get_balances`
    """
    address = await convert.to_address_async(token)
    total_val = await get_tvl(address, block, skip_cache=skip_cache, sync=False)
    if total_val is None:
        return None
    total_supply = await ERC20(address, asynchronous=True).total_supply_readable(
        block, sync=False
    )
    return UsdPrice(total_val / total_supply)


@a_sync.a_sync(default="sync")
async def get_tvl(
    token: AnyAddressType,
    block: Optional[Block] = None,
    skip_cache: bool = ENVS.SKIP_CACHE,
) -> Optional[UsdValue]:
    """
    Calculates the total value locked (TVL) in a Popsicle Finance LP token.

    Args:
        token: The address of the Popsicle LP token.
        block (optional): The block number to query. Defaults to the latest block.
        skip_cache (optional): Whether to skip the cache when fetching TVL. Defaults to :obj:`ENVS.SKIP_CACHE`.

    Returns:
        The total value locked in the LP token in USD, or None if the TVL cannot be determined.

    Example:
        >>> tvl = get_tvl("0xd2C5A739ebfE3E00CFa88A51749d367d7c496CCf", block=14_000_000)
        >>> print(f"{tvl:.2f}")
        1234567.89  # The TVL of the Popsicle LP token in USD

    See Also:
        - :func:`get_price`
        - :func:`get_balances`
    """
    balances: Tuple[WeiBalance, WeiBalance]
    balances = await get_balances(
        token, block, skip_cache=skip_cache, _async_balance_objects=True, sync=False
    )
    return UsdValue(await WeiBalance.value_usd.sum(balances)) if balances else None


@a_sync.a_sync(default="sync")
async def get_balances(
    token: AnyAddressType,
    block: Optional[Block] = None,
    skip_cache: bool = ENVS.SKIP_CACHE,
    _async_balance_objects: bool = False,
) -> Optional[Tuple[WeiBalance, WeiBalance]]:
    """
    Retrieves the balances of the underlying tokens in a Popsicle Finance LP token.

    Args:
        token: The address of the Popsicle LP token.
        block (optional): The block number to query. Defaults to the latest block.
        skip_cache (optional): Whether to skip the cache when fetching balances. Defaults to :obj:`ENVS.SKIP_CACHE`.
        _async_balance_objects (optional): Whether to use asynchronous balance objects. Defaults to False.

    Returns:
        A tuple containing the balances of the two underlying tokens, or None if the balances cannot be determined.

    Example:
        >>> balances = get_balances("0xd2C5A739ebfE3E00CFa88A51749d367d7c496CCf", block=14_000_000)
        >>> if balances:
        ...     balance0, balance1 = balances
        ...     print(f"Token0 Balance: {balance0.readable}, Token1 Balance: {balance1.readable}")
        ... else:
        ...     print("Balances could not be determined.")
        Token0 Balance: 1000.0, Token1 Balance: 2000.0

    Note:
        If the contract probed has the correct method name but the method returns the wrong type for Popsicle,
        an exception "not enough values to unpack (expected 3, got 2)" will be caught, and the function will return None.

    See Also:
        - :func:`get_price`
        - :func:`get_tvl`
    """
    try:
        token0, token1, (balance0, balance1) = await gather_methods(
            await convert.to_address_async(token), _RESERVES_METHODS, block=block
        )
    except Exception as e:
        if call_reverted(e):
            return None
        elif str(e) == "not enough values to unpack (expected 3, got 2)":
            # TODO determine if this is regular behavior when no tvl in pool or if this is bug to fix
            return None
        raise
    balance0 = WeiBalance(
        balance0,
        token0,
        block=block,
        skip_cache=skip_cache,
        asynchronous=_async_balance_objects,
    )
    balance1 = WeiBalance(
        balance1,
        token1,
        block=block,
        skip_cache=skip_cache,
        asynchronous=_async_balance_objects,
    )
    return balance0, balance1
