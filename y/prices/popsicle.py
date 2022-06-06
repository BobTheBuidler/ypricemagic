import logging
from functools import lru_cache
from typing import Optional, Tuple

from async_lru import alru_cache
from multicall import Call
from multicall.utils import await_awaitable, gather
from y import convert
from y.classes.common import WeiBalance
from y.contracts import has_methods_async
from y.datatypes import AnyAddressType, Block, UsdPrice, UsdValue
from y.exceptions import call_reverted
from y.utils.logging import yLazyLogger
from y.utils.raw_calls import _totalSupplyReadable

logger = logging.getLogger(__name__)

@yLazyLogger(logger)
@lru_cache(maxsize=None)
def is_popsicle_lp(token_address: AnyAddressType) -> bool:
    return await_awaitable(is_popsicle_lp_async(token_address))

@yLazyLogger(logger)
@alru_cache(maxsize=None)
async def is_popsicle_lp_async(token_address: AnyAddressType) -> bool:
    # NOTE: contract to check for reference (mainnet): 0xd2C5A739ebfE3E00CFa88A51749d367d7c496CCf
    return await has_methods_async(token_address, ('token0()(address)','token1()(address)','usersAmounts()((uint,uint))'))

@yLazyLogger(logger)
def get_price(token: AnyAddressType, block: Optional[Block] = None) -> Optional[UsdPrice]:
    return await_awaitable(get_price_async(token, block=block))

@yLazyLogger(logger)
async def get_price_async(token: AnyAddressType, block: Optional[Block] = None) -> Optional[UsdPrice]:
    address = convert.to_address(token)
    total_val = await get_tvl_async(address, block)
    if total_val is None:
        return None
    total_supply = await _totalSupplyReadable(address,block)
    return UsdPrice(total_val / total_supply)

@yLazyLogger(logger)
def get_tvl(token: AnyAddressType, block: Optional[Block] = None) -> Optional[UsdValue]:
    return await_awaitable(get_tvl_async(token, block=block))

@yLazyLogger(logger)
async def get_tvl_async(token: AnyAddressType, block: Optional[Block] = None) -> Optional[UsdValue]:
    balances = await get_balances_async(token, block)
    if balances is None:
        return None
    balance0, balance1 = balances
    values = await gather([
        balance0.value_usd_async,
        balance1.value_usd_async,
    ])
    return UsdValue(sum(values))

@yLazyLogger(logger)
def get_balances(token: AnyAddressType, block: Optional[Block] = None) -> Optional[Tuple[WeiBalance,WeiBalance]]:
    return await_awaitable(get_balances_async(token, block=block))
    
@yLazyLogger(logger)
async def get_balances_async(token: AnyAddressType, block: Optional[Block] = None) -> Optional[Tuple[WeiBalance,WeiBalance]]:
    address = convert.to_address(token)
    methods = 'token0()(address)','token1()(address)','usersAmounts()((uint,uint))'
    try:
        token0, token1, (balance0, balance1) = await gather([Call(address, method, block_id=block).coroutine() for method in methods])
    except Exception as e:
        if call_reverted(e):
            return None
        elif str(e) == "not enough values to unpack (expected 3, got 2)":
            # TODO determine if this is regular behavior when no tvl in pool or if this is bug to fix
            return None
        raise
    balance0 = WeiBalance(balance0, token0, block=block)
    balance1 = WeiBalance(balance1, token1, block=block)
    return balance0, balance1
