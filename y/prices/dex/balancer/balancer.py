
import logging
from typing import List, Optional, Union

import a_sync
from a_sync.a_sync.property import HiddenMethodDescriptor
from brownie import chain
from typing_extensions import Self

from y import ENVIRONMENT_VARIABLES as ENVS
from y import exceptions
from y._decorators import stuck_coro_debugger
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.networks import Network
from y.prices.dex.balancer._abc import BalancerABC
from y.prices.dex.balancer.v1 import BalancerV1
from y.prices.dex.balancer.v2 import BalancerV2
from y.utils.cache import optional_async_diskcache


logger = logging.getLogger(__name__)

class BalancerMultiplexer(a_sync.ASyncGenericBase):
    def __init__(self, asynchronous: bool = False) -> None:
        self.asynchronous = asynchronous
    
    @a_sync.aka.property
    async def versions(self) -> List[Union[BalancerV1, BalancerV2]]:
        return [v async for v in a_sync.as_completed([self.__v1__, self.__v2__], aiter=True) if v]
    __versions__: HiddenMethodDescriptor[Self, List[Union[BalancerV1, BalancerV2]]]

    @a_sync.aka.cached_property
    async def v1(self) -> Optional[BalancerV1]:
        try:
            return BalancerV1(asynchronous=self.asynchronous)
        except ImportError:
            return None
    __v1__: HiddenMethodDescriptor[Self, Optional[BalancerV1]]
    
    @a_sync.aka.cached_property
    async def v2(self) -> Optional[BalancerV2]:
        try:
            return BalancerV2(asynchronous=self.asynchronous)
        except ImportError: 
            return None
    __v2__: HiddenMethodDescriptor[Self, Optional[BalancerV2]]

    @stuck_coro_debugger
    @optional_async_diskcache
    async def is_balancer_pool(self, token_address: AnyAddressType) -> bool:
        try:
            await self.get_version(token_address)
            return True
        except exceptions.TokenError:
            return False
    
    @stuck_coro_debugger
    async def get_pool_price(self, token_address: AnyAddressType, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> Optional[UsdPrice]:
        balancer: BalancerABC = await self.get_version(token_address)
        logger.debug("pool %s is from %s", token_address, balancer)
        return UsdPrice(await balancer.get_pool_price(token_address, block, skip_cache=skip_cache, sync=False))
            
    @stuck_coro_debugger
    @a_sync.a_sync(ram_cache_ttl=ENVS.CACHE_TTL)
    async def get_price(self, token_address: AnyAddressType, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> Optional[UsdPrice]:
        if await self.is_balancer_pool(token_address, sync=False):
            return await self.get_pool_price(token_address, block=block, skip_cache=skip_cache, sync=False)

        price = None
        
        if ( # NOTE: Only query v2 if block queried > v2 deploy block plus some extra blocks to build up liquidity
            (chain.id == Network.Mainnet and (not block or block > 12272146 + 100000))
            or (chain.id == Network.Fantom and (not block or block > 16896080))
        ):  # TODO: refactor this out
            v2 = await self.__v2__
            if price := await v2.get_token_price(token_address, block, skip_cache=skip_cache, sync=False):
                logger.debug("balancer v2 -> $%s", price)
                return price

        if not price and chain.id == Network.Mainnet:   
            v1 = await self.__v1__
            if price := await v1.get_token_price(token_address, block, skip_cache=skip_cache, sync=False):
                logger.debug("balancer v1 -> $%s", price)
                return price
    
    # cached forever because not many items
    @a_sync.a_sync(cache_type="memory", ram_cache_ttl=None)  
    async def get_version(self, token_address: AnyAddressType) -> BalancerABC:
        for v in await self.__versions__:
            if await v.is_pool(token_address, sync=False):
                return v
        raise exceptions.TokenError(token_address, "Balancer pool")

balancer_multiplexer = BalancerMultiplexer(asynchronous=True)
