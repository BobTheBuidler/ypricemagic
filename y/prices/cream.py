import logging

from brownie import chain
from y.constants import weth
from y.decorators import log
from y.networks import Network
from y.prices import magic
from y.utils.raw_calls import _totalSupply, raw_call

logger = logging.getLogger(__name__)

@log(logger)
def is_creth(address):
    return chain.id == Network.Mainnet and address == '0xcBc1065255cBc3aB41a6868c22d1f1C573AB89fd'

@log(logger)
def get_price_creth(address, block=None):
    totalBalance = raw_call(address, 'accumulated()', output='int', block=block)
    perShare = totalBalance / _totalSupply(address,block)
    return perShare * magic.get_price(weth,block)
