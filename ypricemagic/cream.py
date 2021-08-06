from brownie import Contract
from ypricemagic import magic
from ypricemagic.constants import weth

def is_creth(address):
    return address == '0xcBc1065255cBc3aB41a6868c22d1f1C573AB89fd'

def get_price_creth(address, block=None):
    contract = Contract(address)
    totalBalance = contract.accumulated(block_identifier = block)
    totalSupply = contract.totalSupply(block_identifier = block)
    perShare = totalBalance / totalSupply
    return perShare * magic.get_price(weth,block)