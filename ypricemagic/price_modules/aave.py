import logging
from functools import lru_cache
from brownie import web3, chain

from multicall import Call, Multicall
from y import Network
from y.contracts import Contract
from ypricemagic import magic
from ypricemagic.utils.raw_calls import raw_call
from ypricemagic.utils.multicall import fetch_multicall

logger = logging.getLogger(__name__)


v1_pools = {
    Network.Mainnet: [
        "0x398eC7346DcD622eDc5ae82352F02bE94C62d119"
    ],
}.get(chain.id, [])

v2_pools = {
    Network.Mainnet: [
        "0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9", # aave v2
        "0x7937D4799803FbBe595ed57278Bc4cA21f3bFfCB", # aave amm v2
    ]
}.get(chain.id, [])


calls = [Call(v1_pool, ['getReserves()(address[])'], [[v1_pool,None]]) for v1_pool in v1_pools]
v1_pools = [Contract(pool) for pool in v1_pools]
v1_reserves = Multicall(calls, _w3=web3)()
v1_atokens = [data['aTokenAddress'] for data in fetch_multicall(*[[v1_pool, 'getReserveData', reserve] for v1_pool, reserve in zip(v1_pools, v1_reserves.values())])]

calls = [Call(v2_pool, ['getReserves()(address[])'], [[v2_pool,None]]) for v2_pool in v2_pools]
v2_pools = [Contract(pool) for pool in v2_pools]
v2_reserves = Multicall(calls, _w3=web3)()
v2_atokens = [data[7] for data in fetch_multicall(*[[v2_pool, 'getReserveData', reserve] for v2_pool, reserve in zip(v2_pools, v2_reserves.values())])]

@lru_cache
def is_atoken_v1(address):
    logger.debug(f'Checking `is_atoken_v1({address})')
    result = address in v1_atokens
    logger.debug(f'`is_atoken_v1({address}` returns `{result}`')
    return result

@lru_cache
def is_atoken_v2(address):
    logger.debug(f'Checking `is_atoken_v2({address})')
    result = address in v2_atokens
    logger.debug(f'`is_atoken_v2({address}` returns `{result}`')
    return result

@lru_cache
def is_atoken(address):
    return is_atoken_v1(address) or is_atoken_v2(address)

def get_price_v1(token, block=None):
    underlying = raw_call(token, 'underlyingAssetAddress()', block=block, output='address')
    return magic.get_price(underlying, block=block)

def get_price_v2(token, block=None):
    underlying = raw_call(token, 'UNDERLYING_ASSET_ADDRESS()',block=block,output='address')
    return magic.get_price(underlying, block=block)

def get_price(token, block=None):
    if is_atoken_v1(token):
        return get_price_v1(token, block)
    if is_atoken_v2(token):
        return get_price_v2(token, block)
