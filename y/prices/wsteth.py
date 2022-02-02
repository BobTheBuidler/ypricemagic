import logging

from brownie import chain
from y.constants import weth
from y.decorators import log
from y.exceptions import UnsupportedNetwork
from y.networks import Network
from y.prices import magic
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)

class wstEth:
    def __init__(self) -> None:
        try: self.address = {
            Network.Mainnet: '0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0'
            }[chain.id]
        except KeyError: self.address = None
    
    @log(logger)
    def get_price(self, block=None):
        share_price = raw_call(self.address, 'stEthPerToken()', output='int', block=block) / 1e18
        return share_price * magic.get_price(weth, block)

wsteth = wstEth()

@log(logger)
def is_wsteth(address):
    try: return address == wsteth.address
    except UnsupportedNetwork: return False

