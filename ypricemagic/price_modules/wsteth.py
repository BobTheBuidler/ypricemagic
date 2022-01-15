from brownie import chain
from y.constants import weth
from y.exceptions import UnsupportedNetwork
from y.networks import Network
from ypricemagic import magic
from ypricemagic.utils.raw_calls import raw_call


class wstEth:
    def __init__(self) -> None:
        try: self.address = {
            Network.Mainnet: '0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0'
            }[chain.id]
        except KeyError: self.address = None
    
    def get_price(self, block=None):
        share_price = raw_call(self.address, 'stEthPerToken()', output='int', block=block) / 1e18
        return share_price * magic.get_price(weth, block)

wsteth = wstEth()

def is_wsteth(address):
    try: return address == wsteth.address
    except UnsupportedNetwork: return False

