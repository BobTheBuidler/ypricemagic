
from brownie.network.contract import Contract

def is_froyo(address):
    return address == '0x4f85Bbf3B0265DCEd4Ec72ebD0358ccCf190F1B3'

def get_price(froyo_address, block=None):
    pool = Contract('0x83E5f18Da720119fF363cF63417628eB0e9fd523')
    return pool.get_virtual_price(block_identifier = block) / 10 ** 18