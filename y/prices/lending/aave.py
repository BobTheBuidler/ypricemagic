import asyncio
import logging
from typing import List, Optional, Union

import a_sync
from brownie import chain
from multicall import Call

from y import convert
from y.classes.common import ERC20, ContractBase
from y.contracts import Contract
from y.datatypes import AddressOrContract, AnyAddressType, Block, UsdPrice
from y.exceptions import ContractNotVerified
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
        "0xcE744a9BAf573167B2CF138114BA32ed7De274Fa", # umee
    ],
    Network.Polygon: [
        "0x8dFf5E27EA6b7AC08EbFdf9eB090F32ee9a30fcf", # aave
    ],
    Network.Avalanche: [
        "0x70BbE4A294878a14CB3CDD9315f5EB490e346163", # blizz
    ]
}.get(chain.id, [])        


class AaveMarketBase(ContractBase):
    def __contains__(self, __o: object) -> bool:
        if not self.asynchronous:
            cls = self.__class__.__name__
            raise RuntimeError(f"'self.asynchronous' must be False to use {cls}.__contains__.\nYou may wish to use {cls}.is_atoken instead.")
        return convert.to_address(__o) in self.atokens
    
    async def contains(self, __o: object) -> bool:
        return convert.to_address(__o) in await self.__atokens__(sync=False)


class AaveMarketV1(AaveMarketBase):
    @a_sync.a_sync(ram_cache_maxsize=256)
    async def underlying(self, token_address: AddressOrContract) -> ERC20:
        underlying = await raw_call(token_address, 'underlyingAssetAddress()',output='address', sync=False)
        return ERC20(underlying)
    
    @a_sync.aka.cached_property
    async def atokens(self) -> List[ERC20]:
        reserves_data = await Call(self.address, ['getReserves()(address[])'], [[self.address,None]]).coroutine()
        reserves_data = reserves_data[self.address]
        reserves_data = fetch_multicall(*[[self.contract, 'getReserveData', reserve] for reserve in reserves_data])
        atokens = [ERC20(reserve['aTokenAddress'], asynchronous=self.asynchronous) for reserve in reserves_data]
        logger.info(f'loaded {len(atokens)} v1 atokens for {self.__repr__()}')
        return atokens


class AaveMarketV2(AaveMarketBase):
    @a_sync.a_sync(ram_cache_maxsize=256)
    async def underlying(self, token_address: AddressOrContract) -> ERC20:
        underlying = await raw_call(token_address, 'UNDERLYING_ASSET_ADDRESS()',output='address', sync=False)
        logger.debug(f"underlying: {underlying}")
        return ERC20(underlying, asynchronous=self.asynchronous)

    @a_sync.aka.cached_property
    async def atokens(self) -> List[ERC20]:
        reserves = await Call(self.address, ['getReservesList()(address[])'], [[self.address,None]]).coroutine()
        reserves = reserves[self.address]
        reserves_data = await asyncio.gather(*[
            Call(
                self.address,
                ['getReserveData(address)((uint256,uint128,uint128,uint128,uint128,uint128,uint40,address,address,address,address,uint8))',reserve],
            ).coroutine()
            for reserve in reserves
        ])

        try:
            atokens = [ERC20(reserve_data[7], asynchronous=self.asynchronous) for reserve_data in reserves_data]
            logger.info(f'loaded {len(atokens)} v2 atokens for {self.__repr__()}')
            return atokens
        except TypeError: # TODO figure out what to do about non verified aave markets
            logger.warning(f'failed to load tokens for {self.__repr__()}')
            return []


class AaveRegistry(a_sync.ASyncGenericSingleton):
    def __init__(self, asynchronous: bool = False) -> None:
        self.asynchronous = asynchronous

    @a_sync.aka.cached_property
    async def pools(self) -> List[Union[AaveMarketV1, AaveMarketV2]]:
        v1, v2 = await asyncio.gather(self.__pools_v1__(sync=False), self.__pools_v2__(sync=False))
        return v1 + v2
    
    @a_sync.aka.cached_property
    async def pools_v1(self) -> List[AaveMarketV1]:
        return [AaveMarketV1(pool, asynchronous=self.asynchronous) for pool in v1_pools]
    
    @a_sync.aka.cached_property
    async def pools_v2(self) -> List[AaveMarketV2]:
        return [AaveMarketV2(pool, asynchronous=self.asynchronous) for pool in v2_pools]
    
    async def pool_for_atoken(self, token_address: AnyAddressType) -> Optional[Union[AaveMarketV1, AaveMarketV2]]:
        pools = await self.__pools__(sync=False)
        for pool in pools:
            if await pool.contains(token_address, sync=False):
                return pool

    def __contains__(self, __o: object) -> bool:
        if self.asynchronous:
            raise RuntimeError(f"'self.asynchronous' must be False to use AaveRegistry.__contains__.\nYou may wish to use AaveRegistry.is_atoken instead.")
        return any(__o in pool for pool in self.pools)

    @a_sync.a_sync(cache_type='memory')
    async def is_atoken(self, token_address: AnyAddressType) -> bool:
        return any(await asyncio.gather(*[pool.contains(token_address, sync=False) for pool in await self.__pools__(sync=False)]))
    
    async def is_wrapped_atoken(self, token_address: AnyAddressType) -> bool:
        try:
            contract = await Contract.coroutine(token_address)
            attrs = "ATOKEN", "AAVE_POOL", "UNDERLYING"
            return all(hasattr(contract, attr) for attr in attrs)
        except ContractNotVerified:
            return False
    
    @a_sync.a_sync(cache_type='memory')
    async def underlying(self, token_address: AddressOrContract) -> ERC20:
        pool: Union[AaveMarketV1, AaveMarketV2] = await self.pool_for_atoken(token_address, sync=False)
        return await pool.underlying(token_address, sync=False)
    
    async def get_price(self, token_address: AddressOrContract, block: Optional[Block] = None) -> UsdPrice:
        underlying = await self.underlying(token_address, sync=False)
        return await underlying.price(block, sync=False)
    
    async def get_price_wrapped(self, token_address: AddressOrContract, block: Optional[Block] = None) -> UsdPrice:
        contract, scale = await asyncio.gather(Contract.coroutine(token_address), ERC20(token_address, asynchronous=True).scale)
        underlying, price_per_share = await asyncio.gather(
            contract.ATOKEN.coroutine(block_identifier=block),
            contract.convertToAssets.coroutine(scale, block_identifier=block),
        )
        price_per_share /= scale
        return price_per_share * await ERC20(underlying, asynchronous=True).price(block)


aave = AaveRegistry(asynchronous=True)
