
import asyncio
import logging
from decimal import Decimal
from typing import Optional

import a_sync

from y import ENVIRONMENT_VARIABLES as ENVS
from y import convert
from y.classes.common import ERC20
from y.contracts import has_methods
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.prices import magic
from y.utils import gather_methods

logger = logging.getLogger(__name__)

@a_sync.a_sync(default='sync', cache_type='memory')
async def is_ib_token(token: AnyAddressType) -> bool:
    return await has_methods(token, ('debtShareToVal(uint)(uint)','debtValToShare(uint)(uint)','token()(address)','totalToken()(uint)','totalSupply()(uint)'), sync=False)

@a_sync.a_sync(default='sync')
async def get_price(token: AnyAddressType, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> UsdPrice:
    address = convert.to_address(token)
    token, total_bal, total_supply = await gather_methods(address, ['token', 'totalToken', 'totalSupply'], block=block)
    token_scale, pool_scale = await asyncio.gather(ERC20(token, asynchronous=True).scale, ERC20(address, asynchronous=True).scale)
    total_bal /= Decimal(token_scale)
    total_supply /= Decimal(pool_scale)
    share_price = total_bal / total_supply
    token_price = await magic.get_price(token, block, skip_cache=skip_cache, sync=False)
    return share_price * token_price
