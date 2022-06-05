
import logging
from typing import Optional

from async_lru import alru_cache
from multicall.utils import await_awaitable, gather
from y import convert
from y.classes.common import ERC20
from y.contracts import Contract, has_methods_async
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.prices import magic
from y.utils.cache import memory
from y.utils.logging import yLazyLogger

logger = logging.getLogger(__name__)

@memory.cache()
@yLazyLogger(logger)
def is_ib_token(token: AnyAddressType) -> bool:
    return await_awaitable(is_ib_token_async(token))

@yLazyLogger(logger)
@alru_cache(maxsize=None)
async def is_ib_token_async(token: AnyAddressType) -> bool:
    return await has_methods_async(token, ('debtShareToVal(uint)(uint)','debtValToShare(uint)(uint)','token()(address)','totalToken()(uint)','totalSupply()(uint)'))

@yLazyLogger(logger)
def get_price(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    return await_awaitable(get_price_async(token, block=block))

@yLazyLogger(logger)
async def get_price_async(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    address = convert.to_address(token)
    contract = Contract(address)
    token, total_bal, total_supply = gather([
        contract.token.coroutine(block_identifier=block),
        contract.totalToken.coroutine(block_identifier=block),
        contract.totalSupply.coroutine(block_identifier=block),
        #fetch_multicall([contract,'token'],[contract,'totalToken'],[contract,'totalSupply'], block=block)
    ])
    token_scale, pool_scale = gather([
        ERC20(token).scale,
        ERC20(address).scale,
    ])
    total_bal /= token_scale
    total_supply /= pool_scale
    share_price = total_bal / total_supply
    token_price = await magic.get_price_async(token, block)
    price = share_price * token_price
    return price
