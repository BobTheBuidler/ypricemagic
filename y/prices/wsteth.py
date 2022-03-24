import logging
from typing import Optional

from brownie import chain
from y import convert
from y.constants import weth
from y.datatypes import UsdPrice
from y.decorators import log
from y.networks import Network
from y.prices import magic
from y.typing import AnyAddressType, Block
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)

class wstEth:
    def __init__(self) -> None:
        try:
            self.address = {
                Network.Mainnet: '0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0'
            }[chain.id]
        except KeyError:
            self.address = None
    
    @log(logger)
    def get_price(self, block: Optional[Block] = None) -> UsdPrice:
        share_price = raw_call(self.address, 'stEthPerToken()', output='int', block=block) / 1e18
        return UsdPrice(share_price * magic.get_price(weth, block))

wsteth = wstEth()

@log(logger)
def is_wsteth(address: AnyAddressType) -> bool:
    if chain.id != Network.Mainnet:
        return False
    address = convert.to_address(address)
    return address == wsteth.address

