from brownie import chain
from ypricemagic.price_modules.balancer.v1.v1 import BalancerV1
from ypricemagic.price_modules.balancer.v2.v2 import BalancerV2

class Balancer:
    def __init__(self) -> None:
        self.versions = []
        try:
            self.v1 = BalancerV1()
            self.versions.append(self.v1)
        except ImportError:
            pass
        try: 
            self.v2 = BalancerV2()
            self.versions.append(self.v2)
        except ImportError:
            pass

    #@memory.cache()
    def is_balancer_pool(self, token_address: str) -> bool:
        return any(v.is_pool(token_address) for v in self.versions)
    
    def get_pool_price(self, token_address: str, block=None):
        if self.v1.is_pool(token_address): return self.v1.get_pool_price(token_address, block)
        if self.v2.is_pool(token_address): return self.v2.get_pool_price(token_address, block)

    def get_price(self, token_address: str, block=None):
        if self.is_balancer_pool(token_address): return self.get_pool_price(token_address, block=block)

        price = None    
        
        if ( # NOTE: Only query v2 if block queried > v2 deploy block plus some extra blocks to build up liquidity
            (chain.id == 1 and (not block or block > 12272146 + 100000))
            or (chain.id == 250 and (not block or block > 16896080))
            ): 
            price = self.v2.get_token_price(token_address, block)

        if not price and chain.id == 1:      
            price = self.v1.get_token_price(token_address, block)
        
        if price: return price

balancer = Balancer()
