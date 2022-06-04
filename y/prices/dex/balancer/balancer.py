import logging
from functools import cached_property, lru_cache
from typing import List, Optional, Union

from async_lru import alru_cache
from brownie import chain
from multicall.utils import await_awaitable, gather
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.networks import Network
from y.prices.dex.balancer.v1 import BalancerV1
from y.prices.dex.balancer.v2 import BalancerV2
from y.utils.logging import yLazyLogger

logger = logging.getLogger(__name__)


class BalancerMultiplexer:
    def __init__(self) -> None:
        pass
    
    def __repr__(self) -> str:
        return "<Balancer>"
    
    @cached_property
    def versions(self) -> List[Union[BalancerV1, BalancerV2]]:
        return [v for v in [self.v1, self.v2] if v]

    @cached_property
    def v1(self) -> Optional[BalancerV1]:
        try: return BalancerV1()
        except ImportError: return None
    
    @cached_property
    def v2(self) -> Optional[BalancerV2]:
        try: return BalancerV2()
        except ImportError: return None

    @yLazyLogger(logger)
    def is_balancer_pool(self, token_address: AnyAddressType) -> bool:
        return await_awaitable(self.is_balancer_pool_async(token_address))

    @yLazyLogger(logger)
    async def is_balancer_pool_async(self, token_address: AnyAddressType) -> bool:
        return any(await gather([v.is_pool_async(token_address) for v in self.versions]))
    
    @yLazyLogger(logger)
    async def get_pool_price(self, token_address: AnyAddressType, block: Optional[Block] = None) -> Optional[UsdPrice]:
        return await_awaitable(self.get_pool_price_async(token_address, block=block))

    @yLazyLogger(logger)
    async def get_pool_price_async(self, token_address: AnyAddressType, block: Optional[Block] = None) -> Optional[UsdPrice]:
        for v in self.versions:
            if await v.is_pool_async(token_address):
                return UsdPrice(await v.get_pool_price_async(token_address, block))

    @yLazyLogger(logger)
    @lru_cache(maxsize=None)
    def get_price(self, token_address: AnyAddressType, block: Optional[Block] = None) -> Optional[UsdPrice]:
        return await_awaitable(self.get_price_async(token_address, block=block))
    
    @yLazyLogger(logger)
    @alru_cache(maxsize=None)
    async def get_price_async(self, token_address: AnyAddressType, block: Optional[Block] = None) -> Optional[UsdPrice]:
        if await self.is_balancer_pool_async(token_address):
            return await self.get_pool_price_async(token_address, block=block)

        price = None    
        
        if ( # NOTE: Only query v2 if block queried > v2 deploy block plus some extra blocks to build up liquidity
            (chain.id == Network.Mainnet and (not block or block > 12272146 + 100000))
            or (chain.id == Network.Fantom and (not block or block > 16896080))
            ): 
            price = await self.v2.get_token_price_async(token_address, block)
            if price:
                logger.debug(f"balancer v2 -> ${price}")
                return price

        if not price and chain.id == Network.Mainnet:      
            price = await self.v1.get_token_price_async(token_address, block)
            if price:
                logger.debug(f"balancer v1 -> ${price}")
                return price
        

balancer_multiplexer = BalancerMultiplexer()
