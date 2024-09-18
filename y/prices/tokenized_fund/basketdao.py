
import asyncio
from decimal import Decimal
from typing import Optional

import a_sync
from brownie.convert.datatypes import EthAddress
from multicall import Call
from web3.exceptions import ContractLogicError

from y import ENVIRONMENT_VARIABLES as ENVS
from y.classes.common import ERC20, WeiBalance
from y.datatypes import Block, UsdPrice


@a_sync.a_sync(default='sync')
async def is_basketdao_index(address: EthAddress) -> bool:
    """
    Check if the given token is a BasketDAO token.

    Args:
        address: The address of the token to check.

    Returns:
        True if the token is a BasketDAO token, False otherwise.

    Example:
        >>> is_bd = is_basketdao("0x0ac58Df435D3dC9F6e079B2C5F358A4b7e861B69")
        >>> print(is_bd)
        True
    """
    try:
        return bool(await Call(address, 'getAssetsAndBalances()(address[],uint[])'))
    except (ContractLogicError, ValueError):
        return False

@a_sync.a_sync(default='sync')
async def get_price(
    address: EthAddress, 
    block: Optional[Block] = None, 
    skip_cache: bool = ENVS.SKIP_CACHE,
) -> UsdPrice:
    """
    Get the price of a BasketDAO token in USD.

    Args:
        address: The address of the BasketDAO token.
        block (optional): The block number to query. Defaults to None (latest).
        skip_cache (optional): Whether to bypass the disk cache. Defaults to :obj:`ENVS.SKIP_CACHE`.

    Returns:
        The price of the BasketDAO token in USD.

    Raises:
        PriceError: If unable to fetch the price.

    Example:
        >>> price = get_price("0x0ac58Df435D3dC9F6e079B2C5F358A4b7e861B69")
        >>> print(price)
        1.05
    """
    balances, total_supply = await asyncio.gather(
        Call(address, 'getAssetsAndBalances()(address[],uint[])',block_id=block),
        ERC20(address, asynchronous=True).total_supply_readable(block=block),
    )
    balances = (WeiBalance(balance, token, block, skip_cache=skip_cache) for token, balance in zip(balances[0], balances[1]))
    tvl = await WeiBalance.value_usd.sum(balances, sync=False)
    return UsdPrice(tvl / Decimal(total_supply))
