import logging
from typing import List, Optional

from async_lru import alru_cache
from brownie import ZERO_ADDRESS
from multicall import Call
from multicall.utils import await_awaitable
from y.contracts import has_method_async
from y.datatypes import Address, AnyAddressType, Block, UsdPrice, UsdValue
from y.erc20 import decimals, totalSupplyReadable
from y.exceptions import call_reverted
from y.prices import magic
from y.utils.logging import yLazyLogger
from y.utils.multicall import multicall_balanceOf
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)


@yLazyLogger(logger)
async def is_pie(token: AnyAddressType) -> bool:
    return await_awaitable(is_pie_async(token))

@yLazyLogger(logger)
@alru_cache(maxsize=None)
async def is_pie_async(token: AnyAddressType) -> bool:
    return await has_method_async(token, "getCap()(uint)")

@yLazyLogger(logger)
def get_price(pie: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    return UsdPrice(tvl(pie, block) / totalSupplyReadable(pie, block))

@yLazyLogger(logger)
def get_tokens(pie_address: Address, block: Optional[Block] = None) -> List[Address]:
    return Call(pie_address, ['getTokens()(address[])'], [['tokens',None]], block_id=block)()['tokens']

@yLazyLogger(logger)
def get_bpool(pie_address: Address, block: Optional[Block] = None) -> Address:
    try:
        bpool = raw_call(pie_address, 'getBPool()', output='address', block=block)
        return bpool if bpool != ZERO_ADDRESS else pie_address
    except Exception as e:
        if not call_reverted(e):
            raise
        return pie_address

@yLazyLogger(logger)
def tvl(pie_address: Address, block: Optional[Block] = None) -> UsdValue:
    tokens = get_tokens(pie_address, block)
    pool = get_bpool(pie_address, block)
    token_balances = multicall_balanceOf(tokens, pool, block=block)
    token_decimals = decimals(tokens, block)
    token_balances = [bal / 10 ** decimal for bal, decimal in zip(token_balances, token_decimals)]
    prices = magic.get_prices(tokens, block, silent=True, dop=1)
    return UsdValue(
        sum(bal * price for bal, price in zip(token_balances, prices))
    )
