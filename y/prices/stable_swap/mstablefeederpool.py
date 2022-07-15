
import logging
from typing import Optional

from async_lru import alru_cache
from multicall.utils import await_awaitable, gather
from y import convert
from y.contracts import Contract, has_methods_async
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.prices import magic
from y.utils.logging import yLazyLogger

logger = logging.getLogger(__name__)


@yLazyLogger(logger)
@alru_cache(maxsize=None)
async def is_mstable_feeder_pool(address: AnyAddressType) -> bool:
    return await has_methods_async(address, ('getPrice()((uint,uint))','mAsset()(address)'))

async def get_price(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    return await_awaitable(get_price_async(token, block))

@yLazyLogger(logger)
async def get_price_async(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    address = convert.to_address(token)
    contract = Contract(address)
    ratio, masset, decimals = await gather([
        contract.getPrice.coroutine(block_identifier=block),
        contract.mAsset.coroutine(block_identifier=block),
        contract.decimals.coroutine(block_identifier=block),
    ])
    ratio = ratio[0] / 10 ** decimals
    underlying_price = await magic.get_price_async(masset,block)
    return UsdPrice(underlying_price * ratio)
