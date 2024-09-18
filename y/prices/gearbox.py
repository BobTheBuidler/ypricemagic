
import asyncio
from decimal import Decimal
from typing import List, Dict

import a_sync
from a_sync.a_sync import HiddenMethodDescriptor
from brownie import chain
from typing_extensions import Self

from y import ENVIRONMENT_VARIABLES as ENVS
from y.classes.common import ERC20, ContractBase
from y.contracts import Contract
from y.datatypes import Address, Block
from y.exceptions import UnsupportedNetwork
from y.networks import Network
from y.utils.cache import a_sync_ttl_cache

registry = "0xA50d4E7D8946a7c90652339CDBd262c375d54D99"

class DieselPool(ContractBase):
    @a_sync.aka.cached_property
    async def contract(self) -> Contract:
        return await Contract.coroutine(self.address)
    __contract__: HiddenMethodDescriptor[Self, Contract]
    
    @a_sync.aka.cached_property
    async def diesel_token(self) -> ERC20:
        contract = await self.__contract__
        try:
            return ERC20(await contract.dieselToken, asynchronous=self.asynchronous)
        except AttributeError: # NOTE: there could be better ways of doing this with hueristics, not sure yet
            return ERC20(self.address, asynchronous=self.asynchronous)
    __diesel_token__: HiddenMethodDescriptor[Self, ERC20]
    
    @a_sync.aka.cached_property
    async def underlying(self) -> ERC20:
        contract = await self.__contract__
        return ERC20(await contract.underlyingToken, asynchronous=self.asynchronous)
    __underlying__: HiddenMethodDescriptor[Self, ERC20]
    
    async def exchange_rate(self, block: Block) -> Decimal:
        underlying: ERC20
        pool, underlying = await asyncio.gather(self.__contract__, self.__underlying__)
        scale = await underlying.__scale__
        return Decimal(await pool.fromDiesel.coroutine(scale, block_identifier=block)) / Decimal(scale)
    
    async def get_price(self, block: Block, skip_cache: bool = ENVS.SKIP_CACHE) -> Decimal:
        underlying, exchange_rate = await asyncio.gather(self.__underlying__, self.exchange_rate(block, sync=False))
        und_price = await underlying.price(block, skip_cache=skip_cache, sync=False)
        return Decimal(und_price) * exchange_rate
        

class Gearbox(a_sync.ASyncGenericBase):
    def __init__(self, asynchronous: bool = False):
        if chain.id != Network.Mainnet:
            raise UnsupportedNetwork("gearbox not supported on this network")
        self.asynchronous = asynchronous
        self._dtokens: Dict[ERC20, DieselPool] = {}            
    
    @a_sync.aka.cached_property
    async def registry(self) -> Contract:
        return await Contract.coroutine(registry)
    
    @a_sync_ttl_cache
    async def pools(self) -> List[DieselPool]:
        registry = await self.registry
        return [DieselPool(pool, asynchronous=self.asynchronous) for pool in await registry.getPools]
    
    async def diesel_tokens(self) -> Dict[ERC20, DieselPool]:
        pools: List[DieselPool] = await self.pools(sync=False)
        return dict(zip(await DieselPool.diesel_token.map(pools).values(pop=True), pools))

    async def is_diesel_token(self, token: Address) -> bool:
        return token in await self.diesel_tokens(sync=False)
    
    async def get_price(self, token: Address, block: Block, skip_cache: bool = ENVS.SKIP_CACHE) -> Decimal:
        dtokens = await self.diesel_tokens()
        return await dtokens[token].get_price(block, skip_cache=skip_cache, sync=False)
    
try:
    gearbox = Gearbox(asynchronous=True)
except:
    gearbox = set()