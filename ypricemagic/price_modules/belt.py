
from brownie import chain
from y.networks import Network
from ypricemagic.utils.raw_calls import raw_call

POOLS = {
    Network.BinanceSmartChain: {
        "0x86aFa7ff694Ab8C985b79733745662760e454169": "0xF16D312d119c13dD27fD0dC814b0bCdcaAa62dfD", # Belt.fi bDAI/bUSDC/bUSDT/bBUSD
        "0x9cb73F20164e399958261c289Eb5F9846f4D1404": "0xAEA4f7dcd172997947809CE6F12018a6D5c1E8b6", # 4Belt
    },
}.get(chain.id, {})


def is_belt_lp(token_address):
    return token_address in POOLS


def get_price(token_address, block=None):
    pool = POOLS[token_address]
    return raw_call(pool, 'get_virtual_price()', output='int', block=block) / 1e18
