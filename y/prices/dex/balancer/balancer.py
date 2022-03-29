import logging
from functools import cached_property
from typing import List, Optional, Union

from brownie import chain
from y.datatypes import UsdPrice
from y.decorators import log
from y.networks import Network
from y.prices.dex.balancer.v1 import BalancerV1
from y.prices.dex.balancer.v2 import BalancerV2
from y.typing import AnyAddressType, Block

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

    @log(logger)
    def is_balancer_pool(self, token_address: AnyAddressType) -> bool:
        return any(v.is_pool(token_address) for v in self.versions)
    
    @log(logger)
    def get_pool_price(self, token_address: AnyAddressType, block: Optional[Block] = None) -> Optional[UsdPrice]:
        for v in self.versions:
            if v.is_pool(token_address):
                return UsdPrice(v.get_pool_price(token_address, block))

    @log(logger)
    def get_price(self, token_address: AnyAddressType, block: Optional[Block] = None) -> Optional[UsdPrice]:
        if self.is_balancer_pool(token_address):
            return self.get_pool_price(token_address, block=block)

        price = None    
        
        if ( # NOTE: Only query v2 if block queried > v2 deploy block plus some extra blocks to build up liquidity
            (chain.id == Network.Mainnet and (not block or block > 12272146 + 100000))
            or (chain.id == Network.Fantom and (not block or block > 16896080))
            ): 
            price = self.v2.get_token_price(token_address, block)
            if price:
                logger.debug(f"balancer v2 -> ${price}")
                return price

        if not price and chain.id == Network.Mainnet:      
            price = self.v1.get_token_price(token_address, block)
            if price:
                logger.debug(f"balancer v1 -> ${price}")
                return price
        

balancer_multiplexer = BalancerMultiplexer()
