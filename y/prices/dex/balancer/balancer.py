import asyncio
import logging
from typing import List, Optional, Union

import a_sync
from brownie import chain

from y.datatypes import AnyAddressType, Block, UsdPrice
from y.decorators import stuck_coro_debugger
from y.networks import Network
from y.prices.dex.balancer.v1 import BalancerV1
from y.prices.dex.balancer.v2 import BalancerV2

logger = logging.getLogger(__name__)


class BalancerMultiplexer(a_sync.ASyncGenericBase):
    def __init__(self, asynchronous: bool = False) -> None:
        self.asynchronous = asynchronous
    
    def __repr__(self) -> str:
        return "<BalancerMuliplexer>"
    
    @a_sync.aka.property
    async def versions(self) -> List[Union[BalancerV1, BalancerV2]]:
        return [v for v in await asyncio.gather(self.v1, self.v2) if v]

    @a_sync.aka.cached_property
    async def v1(self) -> Optional[BalancerV1]:
        try: return BalancerV1(asynchronous=self.asynchronous)
        except ImportError: return None
    
    @a_sync.aka.cached_property
    async def v2(self) -> Optional[BalancerV2]:
        try: return BalancerV2(asynchronous=self.asynchronous)
        except ImportError: return None

    @stuck_coro_debugger
    async def is_balancer_pool(self, token_address: AnyAddressType) -> bool:
        return any(await asyncio.gather(*[v.is_pool(token_address, sync=False) for v in await self.versions]))
    
    @stuck_coro_debugger
    async def get_pool_price(self, token_address: AnyAddressType, block: Optional[Block] = None) -> Optional[UsdPrice]:
        versions: List[Union[BalancerV1, BalancerV2]] = await self.versions
        for v in versions:
            if await v.is_pool(token_address, sync=False):
                return UsdPrice(await v.get_pool_price(token_address, block, sync=False))
            
    @a_sync.a_sync(cache_type='memory')
    @stuck_coro_debugger
    async def get_price(self, token_address: AnyAddressType, block: Optional[Block] = None) -> Optional[UsdPrice]:
        if await self.is_balancer_pool(token_address, sync=False):
            return await self.get_pool_price(token_address, block=block, sync=False)

        price = None
        
        if ( # NOTE: Only query v2 if block queried > v2 deploy block plus some extra blocks to build up liquidity
            (chain.id == Network.Mainnet and (not block or block > 12272146 + 100000))
            or (chain.id == Network.Fantom and (not block or block > 16896080))
            ): 
            v2: BalancerV2 = await self.v2
            price = await v2.get_token_price(token_address, block, sync=False)
            if price:
                logger.debug("balancer v2 -> $%s", price)
                return price

        if not price and chain.id == Network.Mainnet:   
            v1: BalancerV1 = await self.v1   
            price = await v1.get_token_price(token_address, block, sync=False)
            if price:
                logger.debug("balancer v1 -> $%s", price)
                return price

balancer_multiplexer = BalancerMultiplexer(asynchronous=True)
