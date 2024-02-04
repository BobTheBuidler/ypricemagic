
import asyncio
import logging
from decimal import Decimal
from typing import Optional

import a_sync
from brownie import chain

from y import ENVIRONMENT_VARIABLES as ENVS
from y.contracts import Contract
from y.datatypes import Address, Block
from y.networks import Network
from y.prices import magic

logger = logging.getLogger(__name__)

KP3R = "0x1cEB5cB57C4D4E2b2433641b95Dd330A33185A44"
RKP3R = "0xEdB67Ee1B171c4eC66E6c10EC43EDBbA20FaE8e9"

def is_rkp3r(address: Address) -> bool:
    return chain.id == Network.Mainnet and address == RKP3R

@a_sync.a_sync(default="sync")
async def get_price(address: Address, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> Decimal:
    price, discount = await asyncio.gather(magic.get_price(KP3R, block=block, skip_cache=skip_cache, sync=False), get_discount(block))
    return Decimal(price) * (100 - discount) / 100

async def get_discount(block: Optional[Block] = None) -> Decimal:
    rkp3r = await Contract.coroutine(RKP3R)
    discount = Decimal(await rkp3r.discount.coroutine(block_identifier=block))
    logger.debug("discount: %s", discount)
    return discount
