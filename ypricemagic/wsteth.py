from brownie import Contract
from .constants import weth
from .utils.cache import memory
from ypricemagic import magic

wsteth = Contract('0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0')

@memory.cache()
def is_wsteth(address):
    return address == '0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0'

def get_price(address, block=None):
    share_price = wsteth.stEthPerToken(block_identifier = block) / 10 ** 18
    return share_price * magic.get_price(weth, block)