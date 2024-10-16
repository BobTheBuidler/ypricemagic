
import logging
from typing import Optional

import a_sync
from brownie import chain

from y import convert
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.networks import Network
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)

POOL = '0x83E5f18Da720119fF363cF63417628eB0e9fd523'

def is_froyo(token: AnyAddressType) -> bool:
    address = convert.to_address(token)
    return chain.id == Network.Fantom and address == '0x4f85Bbf3B0265DCEd4Ec72ebD0358ccCf190F1B3'

@a_sync.a_sync(default='sync')
async def get_price(token: AnyAddressType, block: Optional[Block] = None) -> Optional[UsdPrice]:
    if not token == POOL:
        return None
    virtual_price = await raw_call(POOL, "get_virtual_price()", block=block, output='int', sync=False)
    return UsdPrice(virtual_price / 10 ** 18)
