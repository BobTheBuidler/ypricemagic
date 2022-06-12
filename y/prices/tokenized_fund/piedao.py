import logging
from typing import List, Optional

from async_lru import alru_cache
from brownie import ZERO_ADDRESS
from multicall import Call
from multicall.utils import await_awaitable, gather
from y.classes.common import ERC20
from y.contracts import has_method_async
from y.datatypes import Address, AnyAddressType, Block, UsdPrice, UsdValue
from y.exceptions import call_reverted
from y.prices import magic
from y.utils.logging import yLazyLogger
from y.utils.raw_calls import raw_call_async

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
    return await_awaitable(get_price_async(pie, block))

async def get_price_async(pie: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    tvl, total_supply = await gather([
        get_tvl(pie, block),
        ERC20(pie).total_supply_readable_async(block),
    ])
    return UsdPrice(tvl / total_supply)

@yLazyLogger(logger)
async def get_tokens(pie_address: Address, block: Optional[Block] = None) -> List[ERC20]:
    tokens = await Call(pie_address, ['getTokens()(address[])'], [['tokens',None]], block_id=block).coroutine()
    tokens = tokens['tokens']
    return [ERC20(t) for t in tokens]

@yLazyLogger(logger)
async def get_bpool(pie_address: Address, block: Optional[Block] = None) -> Address:
    try:
        bpool = await raw_call_async(pie_address, 'getBPool()', output='address', block=block)
        return bpool if bpool != ZERO_ADDRESS else pie_address
    except Exception as e:
        if not call_reverted(e):
            raise
        return pie_address

@yLazyLogger(logger)
async def get_tvl(pie_address: Address, block: Optional[Block] = None) -> UsdValue:
    pool, tokens = await gather([
        get_bpool(pie_address, block),
        get_tokens(pie_address, block),
    ])
    token_balances, token_scales, prices = await gather([
        gather([Call(token, ['balanceOf(address)(uint)', pool], block_id=block).coroutine() for token in tokens]),
        gather([token.scale for token in tokens]),
        magic.get_prices_async(tokens, block),
    ])
    token_balances = [bal / scale for bal, scale in zip(token_balances, token_scales)]
    return UsdValue(
        sum(bal * price for bal, price in zip(token_balances, prices))
    )
