
import asyncio
from decimal import Decimal
from typing import List, Dict

import a_sync
from brownie import chain

from y import ENVIRONMENT_VARIABLES as ENVS
from y.classes.common import ERC20, ContractBase
from y.contracts import Contract
from y.datatypes import Address, Block, UsdPrice
from y.exceptions import UnsupportedNetwork
from y.networks import Network

registry = "0xA50d4E7D8946a7c90652339CDBd262c375d54D99"

class DieselPool(ContractBase):
    @a_sync.aka.cached_property
    async def contract(self) -> Contract:
        return await Contract.coroutine(self.address)
    
    @a_sync.aka.cached_property
    async def diesel_token(self) -> ERC20:
        contract = await self.__contract__(sync=False)
        return ERC20(await contract.dieselToken.coroutine(), asynchronous=self.asynchronous)
    
    @a_sync.aka.cached_property
    async def underlying(self) -> ERC20:
        contract = await self.__contract__(sync=False)
        return ERC20(await contract.underlyingToken.coroutine(), asynchronous=self.asynchronous)
    
    async def exchange_rate(self, block: Block) -> Decimal:
        pool, underlying = await asyncio.gather(self.__contract__(sync=False), self.__underlying__(sync=False))
        scale = await underlying.__scale__(sync=False)
        return Decimal(await pool.fromDiesel.coroutine(scale, block_identifier=block)) / Decimal(scale)
    
    async def get_price(self, block: Block) -> Decimal:
        underlying, exchange_rate = await asyncio.gather(self.__underlying__(sync=False), self.exchange_rate(block, sync=False))
        und_price = await underlying.price(block, sync=False)
        return Decimal(und_price) * exchange_rate
        

class Gearbox(a_sync.ASyncGenericBase):
    def __init__(self, asynchronous: bool = False):
        if chain.id == Network.Mainnet:
            self.asynchronous = asynchronous
            self._dtokens: Dict[ERC20, DieselPool] = {}
        else:
            raise UnsupportedNetwork()
    
    @a_sync.aka.cached_property
    async def registry(self) -> Contract:
        return await Contract.coroutine(registry)
    
    @a_sync.a_sync(ram_cache_ttl=ENVS.CACHE_TTL)
    async def pools(self) -> List[DieselPool]:
        registry = await self.registry
        return [DieselPool(pool, asynchronous=self.asynchronous) for pool in await registry.getPools.coroutine()]
    
    async def diesel_tokens(self) -> Dict[ERC20, DieselPool]:
        pools = await self.pools(sync=False)
        dtokens = await asyncio.gather(*[pool.__diesel_token__(sync=False) for pool in pools])
        return dict(zip(dtokens, pools))

    async def is_diesel_token(self, token: Address) -> bool:
        return token in await self.diesel_tokens(sync=False)
    
    async def get_price(self, token: Address, block: Block) -> Decimal:
        dtokens = await self.diesel_tokens()
        return await dtokens[token].get_price(block, sync=False)
    
try:
    gearbox = Gearbox(asynchronous=True)
except:
    gearbox = set()