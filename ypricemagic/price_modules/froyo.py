
from brownie import chain
from y.networks import Network
from ypricemagic.utils.raw_calls import raw_call


def is_froyo(address):
    return chain.id == Network.Fantom and address == '0x4f85Bbf3B0265DCEd4Ec72ebD0358ccCf190F1B3'

def get_price(froyo_address, block=None):
    pool = '0x83E5f18Da720119fF363cF63417628eB0e9fd523'
    return raw_call(pool, "get_virtual_price()", block=block, output='int') / 1e18
