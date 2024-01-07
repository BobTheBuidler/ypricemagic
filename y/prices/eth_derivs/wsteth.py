import asyncio
import logging
from decimal import Decimal
from typing import Optional

import a_sync
from brownie import chain

from y import ENVIRONMENT_VARIABLES as ENVS
from y import convert
from y.constants import weth
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.networks import Network
from y.prices import magic
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)

class wstEth(a_sync.ASyncGenericBase):
    def __init__(self, asynchronous: bool = False) -> None:
        self.asynchronous = asynchronous
        try:
            self.address = {
                Network.Mainnet: '0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0'
            }[chain.id]
            self.wrapped_for_curve = {
                Network.Mainnet: '0xb82CFa4325568748506dC7cF267857Ff1e3b8d39'
            }[chain.id]
        except KeyError:
            self.address = None

    async def get_price(self, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> UsdPrice:
        share_price, weth_price = await asyncio.gather(
            raw_call(self.address, 'stEthPerToken()', output='int', block=block, sync=False),
            magic.get_price(weth, block, skip_cache=skip_cache, sync=False),
        )
        share_price /= Decimal(10 ** 18)
        return UsdPrice(share_price * Decimal(float(weth_price)))

wsteth = wstEth(asynchronous=True)

def is_wsteth(address: AnyAddressType) -> bool:
    return chain.id == Network.Mainnet and convert.to_address(address) in [wsteth.address, wsteth.wrapped_for_curve]
