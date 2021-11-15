from brownie import Contract

from ypricemagic.utils.multicall2 import fetch_multicall
from .utils.cache import memory

POOLS = {
    "0x86aFa7ff694Ab8C985b79733745662760e454169": Contract("0xF16D312d119c13dD27fD0dC814b0bCdcaAa62dfD"), # Belt.fi bDAI/bUSDC/bUSDT/bBUSD
    "0x9cb73F20164e399958261c289Eb5F9846f4D1404": Contract("0xAEA4f7dcd172997947809CE6F12018a6D5c1E8b6"), # 4Belt
}

@memory.cache()
def is_belt_lp(token_address):
    return token_address in POOLS

def get_price(token_address, block=None):
    pool = POOLS[token_address]
    return pool.get_virtual_price(block_identifier=block) / 10 ** 18
