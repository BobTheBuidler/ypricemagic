
import asyncio
import logging
from typing import Optional

import a_sync

from y import ENVIRONMENT_VARIABLES as ENVS
from y import convert
from y.classes.common import ERC20
from y.contracts import Contract, has_methods
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.prices import magic

logger = logging.getLogger(__name__)


@a_sync.a_sync(default='sync', cache_type='memory', ram_cache_ttl=5*60)
async def is_mstable_feeder_pool(address: AnyAddressType) -> bool:
    return await has_methods(address, ('getPrice()((uint,uint))', 'mAsset()(address)'), sync=False)

@a_sync.a_sync(default='sync')
async def get_price(token: AnyAddressType, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> UsdPrice:
    address = convert.to_address(token)
    contract = await Contract.coroutine(address)
    ratio, masset, scale = await asyncio.gather(
        contract.getPrice.coroutine(block_identifier=block),
        contract.mAsset.coroutine(block_identifier=block),
        ERC20(address, asynchronous=True).scale,
    )
    ratio = ratio[0] / scale
    underlying_price = await magic.get_price(masset, block, skip_cache=skip_cache, sync=False)
    return UsdPrice(underlying_price * ratio)
