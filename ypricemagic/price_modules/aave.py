import logging
from functools import lru_cache

from brownie import chain, web3
from multicall import Call, Multicall
from y.contracts import Contract
from y.decorators import log
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
        "0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9", # aave
        "0x7937D4799803FbBe595ed57278Bc4cA21f3bFfCB", # aave amm
    ],
    Network.Polygon: [
        "0x8dFf5E27EA6b7AC08EbFdf9eB090F32ee9a30fcf", # aave
    ],
    Network.Avalanche: [
        "0x70BbE4A294878a14CB3CDD9315f5EB490e346163", # blizz
    ]
}.get(chain.id, [])


class Aave:
    def __init__(self) -> None:
        if len(v1_pools):
            calls_v1 = [Call(v1_pool, ['getReserves()(address[])'], [[v1_pool,None]]) for v1_pool in v1_pools]
            reserves_v1 = {Contract(pool): reserves for pool, reserves in Multicall(calls_v1, _w3=web3)().items()}
            multicall_v1 = fetch_multicall(*[
                [v1_pool, 'getReserveData', reserve]
                for v1_pool, reserves in reserves_v1.items() for reserve in reserves
            ])
            self.atokens_v1 = [reserve['aTokenAddress'] for reserve in multicall_v1]
            logger.info(f'loaded {len(self.atokens_v1)} v1 atokens')

        if len(v2_pools):
            calls_v2 = [Call(v2_pool, ['getReservesList()(address[])'], [[v2_pool,None]]) for v2_pool in v2_pools]
            reserves_v2 = {pool: reserves for pool, reserves in Multicall(calls_v2, _w3=web3)().items()}

            try:
                calls_v2 = [
                    Call(
                        v2_pool,
                        ['getReserveData(address)((uint256,uint128,uint128,uint128,uint128,uint128,uint40,address,address,address,address,uint8))',reserve],
                        [[v2_pool + reserve, None]]
                    )
                    for v2_pool, reserves in reserves_v2.items() for reserve in reserves
                ]
                self.atokens_v2 = [reserve_data[7] for reserve_data in Multicall(calls_v2, _w3=web3)().values()]
                logger.info(f'loaded {len(self.atokens_v2)} v2 atokens')
            except TypeError: # TODO figure out what to do about non verified aave markets
                self.atokens_v2 = []

    @log(logger)
    @lru_cache
    def is_atoken(self,token_address: str):
        logger.debug(f'Checking `is_atoken({token_address})')
        result = self.is_atoken_v2(token_address) or self.is_atoken_v1(token_address)
        logger.debug(f'`is_atoken({token_address}` returns `{result}`')
        return result

    @log(logger)
    def get_price(self, token_address: str, block=None):
        logger.debug(f'Checking `aave.get_price({token_address}, {block})`')
        if self.is_atoken_v1(token_address):
            price = self.get_price_v1(token_address, block)
        if self.is_atoken_v2(token_address):
            price = self.get_price_v2(token_address, block)
        logger.debug(f'`aave.get_price({token_address}, {block})` returns `{price}`')
        return price

    @log(logger)
    def is_atoken_v1(self,token_address):
        logger.debug(f'Checking `is_atoken_v1({token_address})')
        if not hasattr(self, 'atokens_v1'): result = False
        else: result = token_address in self.atokens_v1
        logger.debug(f'`is_atoken_v1({token_address}` returns `{result}`')
        return result

    @log(logger)
    def is_atoken_v2(self,token_address: str):
        logger.debug(f'Checking `is_atoken_v2({token_address})')
        if not hasattr(self, 'atokens_v2'): result = False
        else: result = token_address in self.atokens_v2
        logger.debug(f'`is_atoken_v2({token_address}` returns `{result}`')
        return result

    @log(logger)
    def get_price_v1(self,token_address: str, block=None):
        underlying = raw_call(token_address, 'underlyingAssetAddress()', block=block, output='address')
        return magic.get_price(underlying, block=block)

    @log(logger)
    def get_price_v2(self,token_address: str, block=None):
        underlying = raw_call(token_address, 'UNDERLYING_ASSET_ADDRESS()',block=block,output='address')
        return magic.get_price(underlying, block=block)

aave = Aave()