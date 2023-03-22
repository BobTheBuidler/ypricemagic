
import logging
from typing import Optional

import a_sync
from brownie import chain

from y import convert
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.networks import Network
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)

POOLS = {
    Network.BinanceSmartChain: {
        "0x86aFa7ff694Ab8C985b79733745662760e454169": "0xF16D312d119c13dD27fD0dC814b0bCdcaAa62dfD", # Belt.fi bDAI/bUSDC/bUSDT/bBUSD
        "0x9cb73F20164e399958261c289Eb5F9846f4D1404": "0xAEA4f7dcd172997947809CE6F12018a6D5c1E8b6", # 4Belt
    },
}.get(chain.id, {})


def is_belt_lp(token: AnyAddressType) -> bool:
    address = convert.to_address(token)
    return address in POOLS
 
@a_sync.a_sync(default='sync')
async def get_price(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    address = convert.to_address(token)
    pool = POOLS[address]
    virtual_price = await raw_call(pool, 'get_virtual_price()', output='int', block=block, sync=False)
    return UsdPrice(virtual_price / 1e18)
