import logging
from functools import cached_property, lru_cache
from typing import List, Union

from brownie import chain, convert, web3
from multicall import Call, Multicall
from y.classes.common import ERC20, ContractBase
from y.decorators import log
from y.networks import Network
from y.utils.multicall import fetch_multicall
from y.utils.raw_calls import raw_call

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


class AaveMarketBase(ContractBase):
    def __init__(self, address: str, *args, **kwargs):
        super().__init__(address, *args, **kwargs)
    
    def __contains__(self, __o: object) -> bool:
        return convert.to_address(__o) in self.atokens


class AaveMarketV1(AaveMarketBase):
    def __init__(self, address: str, *args, **kwargs):
        super().__init__(address, *args, **kwargs)
    
    def __repr__(self) -> str:
        return f"<AaveMarketV1 '{self.address}'>"
    
    @log(logger)
    @lru_cache
    def underlying(self, token_address: str) -> ERC20:
        return ERC20(raw_call(token_address, 'underlyingAssetAddress()',output='address'))
    
    @cached_property
    @log(logger)
    def atokens(self) -> List[ERC20]:
        reserves_data = Call(self.address, ['getReserves()(address[])'], [[self.address,None]], _w3=web3)()[self.address]
        reserves_data = fetch_multicall(*[[self.contract, 'getReserveData', reserve] for reserve in reserves_data])
        atokens = [ERC20(reserve['aTokenAddress']) for reserve in reserves_data]
        logger.info(f'loaded {len(atokens)} v1 atokens for {self.__repr__()}')
        return atokens


class AaveMarketV2(AaveMarketBase):
    def __init__(self, address: str, *args, **kwargs):
        super().__init__(address, *args, **kwargs)
    
    def __repr__(self) -> str:
        return f"<AaveMarketV2 '{self.address}'>"
    
    @log(logger)
    @lru_cache
    def underlying(self, token_address: str) -> ERC20:
        return ERC20(raw_call(token_address, 'UNDERLYING_ASSET_ADDRESS()',output='address'))

    @cached_property
    @log(logger)
    def atokens(self) -> List[ERC20]:
        reserves = Call(self.address, ['getReservesList()(address[])'], [[self.address,None]], _w3=web3)()[self.address]
        calls = [
            Call(
                self.address,
                ['getReserveData(address)((uint256,uint128,uint128,uint128,uint128,uint128,uint40,address,address,address,address,uint8))',reserve],
                [[reserve, None]]
            )
            for reserve in reserves
        ]

        try:
            atokens = [ERC20(reserve_data[7]) for reserve_data in Multicall(calls, _w3=web3)().values()]
            logger.info(f'loaded {len(atokens)} v2 atokens for {self.__repr__()}')
            return atokens
        except TypeError: # TODO figure out what to do about non verified aave markets
            logger.error(f'failed to load tokens for {self.__repr__()}')
            return []


class AaveRegistry:
    def __init__(self) -> None:
        pass

    @cached_property
    def pools(self) -> List[Union[AaveMarketV1, AaveMarketV2]]:
        return self.pools_v1 + self.pools_v2
    
    @cached_property
    def pools_v1(self) -> List[AaveMarketV1]:
        return [AaveMarketV1(pool) for pool in v1_pools]
    
    @cached_property
    def pools_v2(self) -> List[AaveMarketV2]:
        return [AaveMarketV2(pool) for pool in v2_pools]
    
    @log(logger)
    def pool_for_token(self, token_address: str) -> Union[AaveMarketV1, AaveMarketV2]:
        for pool in self.pools:
            if token_address in pool:
                return pool

    def __contains__(self, __o: object) -> bool:
        return any(__o in pool for pool in self.pools)

    @log(logger)
    @lru_cache
    def is_atoken(self,token_address: str):
        return token_address in self
    
    @log(logger)
    @lru_cache
    def underlying(self, token_address: str) -> ERC20:
        pool = self.pool_for_token(token_address)
        return pool.underlying(token_address)
    
    @log(logger)
    def get_price(self, token_address: str, block=None):
        return self.underlying(token_address).price(block)


aave = AaveRegistry()
