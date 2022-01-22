import logging
from functools import lru_cache

from brownie import chain, web3
from multicall import Call, Multicall
from y.contracts import Contract
from y.networks import Network
from ypricemagic import magic
from ypricemagic.utils.multicall import fetch_multicall
from ypricemagic.utils.raw_calls import raw_call

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


class Aave:
    def __init__(self) -> None:
        if len(v1_pools):
            calls_v1 = [Call(v1_pool, ['getReserves()(address[])'], [[v1_pool,None]]) for v1_pool in v1_pools]
            reserves_v1 = {Contract(pool): reserves for pool, reserves in Multicall(calls_v1, _w3=web3)()}
            self.atokens_v1 = [data['aTokenAddress'] for data in fetch_multicall(*[[v1_pool, 'getReserveData', reserve] for v1_pool, reserve in reserves_v1.items()])]
            logger.info(f'loaded {len(self.atokens_v1)} v1 atokens')

        if len(v2_pools):
            calls_v2 = [Call(v2_pool, ['getReservesList()(address[])'], [[v2_pool,None]]) for v2_pool in v2_pools]
            reserves_v2 = {Contract(pool): reserves for pool, reserves in Multicall(calls_v2, _w3=web3)()}
            self.atokens_v2 = [data[7] for data in fetch_multicall(*[[v2_pool, 'getReserveData', reserve] for v2_pool, reserve in reserves_v2.items()])]
            logger.info(f'loaded {len(self.atokens_v2)} v2 atokens')

    @lru_cache
    def is_atoken(self,token_address: str):
        logger.debug(f'Checking `is_atoken({token_address})')
        result = self.is_atoken_v2(token_address) or self.is_atoken_v1(token_address)
        logger.debug(f'`is_atoken({token_address}` returns `{result}`')
        return result

    def get_price(self, token_address: str, block=None):
        logger.debug(f'Checking `aave.get_price({token_address}, {block})`')
        if self.is_atoken_v1(token_address):
            price = self.get_price_v1(token_address, block)
        if self.is_atoken_v2(token_address):
            price = self.get_price_v2(token_address, block)
        logger.debug(f'`aave.get_price({token_address}, {block})` returns `{price}`')
        return price

    def is_atoken_v1(self,token_address):
        logger.debug(f'Checking `is_atoken_v1({token_address})')
        result = token_address in self.atokens_v1
        logger.debug(f'`is_atoken_v1({token_address}` returns `{result}`')
        return result

    def is_atoken_v2(self,token_address: str):
        logger.debug(f'Checking `is_atoken_v2({token_address})')
        result = token_address in self.atokens_v2
        logger.debug(f'`is_atoken_v2({token_address}` returns `{result}`')
        return result

    def get_price_v1(self,token_address: str, block=None):
        underlying = raw_call(token_address, 'underlyingAssetAddress()', block=block, output='address')
        return magic.get_price(underlying, block=block)

    def get_price_v2(self,token_address: str, block=None):
        underlying = raw_call(token_address, 'UNDERLYING_ASSET_ADDRESS()',block=block,output='address')
        return magic.get_price(underlying, block=block)

aave = Aave()