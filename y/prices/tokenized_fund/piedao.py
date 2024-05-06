import asyncio
import logging
from decimal import Decimal
from typing import List, Optional

import a_sync
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


@a_sync.a_sync(default='sync', cache_type='memory')
async def is_pie(token: AnyAddressType) -> bool:
    return await has_method(token, "getCap()(uint)", sync=False)

@a_sync.a_sync(default='sync')
async def get_price(pie: AnyAddressType, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> UsdPrice:
    tvl, total_supply = await asyncio.gather(
        get_tvl(pie, block, skip_cache=skip_cache),
        ERC20(pie, asynchronous=True).total_supply_readable(block),
    )
    return UsdPrice(tvl / total_supply)

async def get_tokens(pie_address: Address, block: Optional[Block] = None) -> List[ERC20]:
    return [ERC20(t) for t in await Call(pie_address, ['getTokens()(address[])'], block_id=block)]

async def get_bpool(pie_address: Address, block: Optional[Block] = None) -> Address:
    try:
        bpool = await raw_call(pie_address, 'getBPool()', output='address', block=block, sync=False)
        return bpool if bpool != ZERO_ADDRESS else pie_address
    except Exception as e:
        if not call_reverted(e):
            raise
        return pie_address

async def get_tvl(pie_address: Address, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> UsdValue:
    tokens: List[ERC20]
    pool, tokens = await asyncio.gather(get_bpool(pie_address, block), get_tokens(pie_address, block))
    return await a_sync.map(get_value, tokens, bpool=pool, block=block, skip_cache=skip_cache).sum(pop=True, sync=False)

async def get_balance(bpool: Address, token: ERC20, block: Optional[Block] = None) -> Decimal:
    balance, scale = await asyncio.gather(Call(token.address, ['balanceOf(address)(uint)', bpool], block_id=block), token.__scale__)
    return Decimal(balance) / scale

async def get_value(bpool: Address, token: ERC20, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> UsdValue:
    balance, price = await asyncio.gather(get_balance(bpool, token, block), token.price(block, skip_cache=skip_cache, sync=False))
    return UsdValue(balance * Decimal(price))
