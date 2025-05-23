from decimal import Decimal
from typing import Optional

from a_sync import a_sync, cgather
from eth_typing import ChecksumAddress
from multicall import Call
from web3.exceptions import ContractLogicError

from y import ENVIRONMENT_VARIABLES as ENVS
from y.classes.common import ERC20, WeiBalance
from y.datatypes import Block, UsdPrice


@a_sync(default="sync")
async def is_basketdao_index(address: ChecksumAddress) -> bool:
    """
    Check if the given token is a BasketDAO token by attempting to call the `getAssetsAndBalances` method.

    Args:
        address: The address of the token to check.

    Returns:
        True if the token is a BasketDAO token, False otherwise.

    Example:
        >>> is_bd = is_basketdao_index("0x0ac58Df435D3dC9F6e079B2C5F358A4b7e861B69")
        >>> print(is_bd)
        True

    Notes:
        Any exceptions (e.g. :exc:`ContractLogicError` or :exc:`ValueError`) encountered during the call are caught,
        causing the function to return False.

    See Also:
        - :func:`get_price` for fetching the price of a BasketDAO token.
    """
    try:
        # Attempt to call the method and check if it returns a valid response
        return bool(await Call(address, "getAssetsAndBalances()(address[],uint[])"))
    except (ContractLogicError, ValueError):
        return False


@a_sync(default="sync")
async def get_price(
    address: ChecksumAddress,
    block: Optional[Block] = None,
    skip_cache: bool = ENVS.SKIP_CACHE,
) -> UsdPrice:
    """
    Get the price of a BasketDAO token in USD by calculating the total value of its assets.

    Args:
        address: The address of the BasketDAO token.
        block (optional): The block number to query. Defaults to None (latest).
        skip_cache (optional): Whether to bypass the disk cache. Defaults to :obj:`ENVS.SKIP_CACHE`.

    Example:
        >>> price = get_price("0x0ac58Df435D3dC9F6e079B2C5F358A4b7e861B69")
        >>> print(price)
        1.05

    Notes:
        This function does not explicitly raise any exceptions such as a PriceError.
        Underlying errors during asset data retrieval will propagate, so callers should handle exceptions as needed.

    See Also:
        - :func:`is_basketdao_index` for checking if a token is a BasketDAO token.
    """
    balances, total_supply = await cgather(
        Call(address, "getAssetsAndBalances()(address[],uint[])", block_id=block),
        ERC20(address, asynchronous=True).total_supply_readable(block=block),
    )
    balances = (
        WeiBalance(balance, token, block, skip_cache=skip_cache)
        for token, balance in zip(balances[0], balances[1])
    )
    tvl = await WeiBalance.value_usd.sum(balances, sync=False)
    return UsdPrice(tvl / Decimal(total_supply))
