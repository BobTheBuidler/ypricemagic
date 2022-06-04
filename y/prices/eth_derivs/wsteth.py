import logging
from typing import Optional

from brownie import chain
from multicall.utils import await_awaitable, gather
from y import convert
from y.constants import weth
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.networks import Network
from y.prices import magic
from y.utils.logging import yLazyLogger
from y.utils.raw_calls import raw_call_async

logger = logging.getLogger(__name__)

class wstEth:
    def __init__(self) -> None:
        try:
            self.address = {
                Network.Mainnet: '0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0'
            }[chain.id]
        except KeyError:
            self.address = None
    
    @yLazyLogger(logger)
    def get_price(self, block: Optional[Block] = None) -> UsdPrice:
        return await_awaitable(self.get_price_async(block=block))

    @yLazyLogger(logger)
    async def get_price_async(self, block: Optional[Block] = None) -> UsdPrice:
        share_price, weth_price = await gather([
            raw_call_async(self.address, 'stEthPerToken()', output='int', block=block),
            magic.get_price_async(weth, block),
        ])
        share_price /= 1e18
        return UsdPrice(share_price * weth_price)

wsteth = wstEth()

@yLazyLogger(logger)
def is_wsteth(address: AnyAddressType) -> bool:
    if chain.id != Network.Mainnet:
        return False
    address = convert.to_address(address)
    return address == wsteth.address

