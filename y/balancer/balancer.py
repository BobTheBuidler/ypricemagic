import logging
from functools import cached_property
from typing import List, Union

from brownie import chain
from y.balancer.v1.v1 import BalancerV1
from y.balancer.v2.v2 import BalancerV2
from y.decorators import log
from y.networks import Network

logger = logging.getLogger(__name__)


class Balancer:
    def __init__(self) -> None:
        pass
    
    def __repr__(self) -> str:
        return "<Balancer>"
    
    @cached_property
    def versions(self) -> List[Union[BalancerV1, BalancerV2]]:
        return [v for v in [self.v1, self.v2] if v]

    @cached_property
    def v1(self):
        try: return BalancerV1()
        except ImportError: return None
    
    @cached_property
    def v2(self):
        try: return BalancerV2()
        except ImportError: return None

    @log(logger)
    def is_balancer_pool(self, token_address: str) -> bool:
        return any(v.is_pool(token_address) for v in self.versions)
    
    @log(logger)
    def get_pool_price(self, token_address: str, block=None):
        for v in self.versions:
            if v.is_pool(token_address): return v.get_pool_price(token_address, block)

    @log(logger)
    def get_price(self, token_address: str, block=None):
        if self.is_balancer_pool(token_address): return self.get_pool_price(token_address, block=block)

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
        

balancer = Balancer()
