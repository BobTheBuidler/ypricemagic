import asyncio
import logging
from typing import List, Optional

import a_sync
from brownie import ZERO_ADDRESS
from multicall import Call

from y.classes.common import ERC20
from y.contracts import has_method
from y.datatypes import Address, AnyAddressType, Block, UsdPrice, UsdValue
from y.exceptions import call_reverted
from y.prices import magic
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)


@a_sync.a_sync(default='sync', cache_type='memory')
async def is_pie(token: AnyAddressType) -> bool:
    return await has_method(token, "getCap()(uint)", sync=False)

@a_sync.a_sync(default='sync')
async def get_price(pie: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    tvl, total_supply = await asyncio.gather(
        get_tvl(pie, block),
        # TODO: debug why we need sync kwarg here
        ERC20(pie, asynchronous=True).total_supply_readable(block, sync=False),
    )
    return UsdPrice(tvl / total_supply)

async def get_tokens(pie_address: Address, block: Optional[Block] = None) -> List[ERC20]:
    tokens = await Call(pie_address, ['getTokens()(address[])'], [['tokens',None]], block_id=block).coroutine()
    tokens = tokens['tokens']
    return [ERC20(t) for t in tokens]

async def get_bpool(pie_address: Address, block: Optional[Block] = None) -> Address:
    try:
        bpool = await raw_call(pie_address, 'getBPool()', output='address', block=block, sync=False)
        return bpool if bpool != ZERO_ADDRESS else pie_address
    except Exception as e:
        if not call_reverted(e):
            raise
        return pie_address

async def get_tvl(pie_address: Address, block: Optional[Block] = None) -> UsdValue:
    tokens: List[ERC20]
    pool, tokens = await asyncio.gather(
        get_bpool(pie_address, block),
        get_tokens(pie_address, block),
    )
    token_balances, token_scales, prices = await asyncio.gather(
        asyncio.gather(*[Call(token.address, ['balanceOf(address)(uint)', pool], block_id=block).coroutine() for token in tokens]),
        asyncio.gather(*[token.__scale__(sync=False) for token in tokens]),
        magic.get_prices(tokens, block, sync=False),
    )
    token_balances = [bal / scale for bal, scale in zip(token_balances, token_scales)]
    return UsdValue(
        sum(bal * price for bal, price in zip(token_balances, prices))
    )
