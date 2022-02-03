import logging
from typing import Dict

from brownie import convert
from cachetools.func import ttl_cache
from y.decorators import log
from y.exceptions import contract_not_verified
from y.uniswap.protocols import UNISWAPS
from y.uniswap.v1 import UniswapV1
from y.uniswap.v2.pool import NotAUniswapV2Pool, UniswapPoolV2
from y.uniswap.v2.router import UniswapRouterV2
from y.utils.logging import gh_issue_request
from y.utils.multicall import multicall_same_func_no_input

logger = logging.getLogger(__name__)

# NOTE: If this is failing to pull a price for a token you need, it's likely because that token requires a special swap path.
#       Please add a viable swap path to ..protocols to fetch price data successfully.

class Uniswap:
    def __init__(self) -> None:
        self.routers = {}
        for name in UNISWAPS:
            try: self.routers[name] = UniswapRouterV2(UNISWAPS[name]['router'])
            except ValueError as e: # TODO do this better
                if contract_not_verified(e): continue
                else: raise
        self.factories = [UNISWAPS[name]['factory'] for name in UNISWAPS]
        self.v1 = UniswapV1()

    @log(logger)
    def is_uniswap_pool(self, token_address: str) -> bool:
        try:
            pool = UniswapPoolV2(token_address)
            is_pool = all(pool.get_pool_details())
            if is_pool and pool.factory not in self.factories:
                gh_issue_request(f'UniClone Factory {pool.factory} is unknown to ypricemagic.', logger)
                self.factories.append(pool.factory)
            return is_pool

        except NotAUniswapV2Pool: return False

    @log(logger)
    def get_price_v1(self, token_address: str, block: int = None):
        return self.v1.get_price(token_address, block)
    
    @log(logger)
    @ttl_cache(ttl=600)
    def lp_price(self, token_address: str, block: int = None) -> float:
        """ Get Uniswap/Sushiswap LP token price. """
        return UniswapPoolV2(token_address).get_price(block=block)
    
    @log(logger)
    @ttl_cache(ttl=36000)
    def get_price(self, token_in: str, block: int = None, protocol: str = None) -> float:
        """
        Calculate a price based on Uniswap Router quote for selling one `token_in`.
        Always finds the deepest swap path for `token_in`.
        """
        token_in = convert.to_address(token_in)

        if protocol:
            return self.routers[protocol].get_price(token_in, block=block)

        for router in self.deepest_routers(token_in, block=block):
            # tries each known router from most to least liquid
            # returns the first price we get back, almost always from the deepest router
            price = router.get_price(token_in, block=block)
            if price: return price
    

    @log(logger)
    def deepest_router(self, token_in: str, block: int = None) -> UniswapRouterV2:
        token_in = convert.to_address(token_in)

        for router in self.deepest_routers(token_in, block=block):
            return router # will return first router in the dict, or None if no supported routers


    @log(logger)
    def deepest_routers(self, token_in: str, block: int = None) -> Dict[UniswapRouterV2,str]:
        token_in = convert.to_address(token_in)
        deepest_pool_by_router = {router: router.deepest_pool(token_in, block) for router in self.routers.values()}
        deepest_pool_by_router = {router: pool for router, pool in deepest_pool_by_router.items() if pool is not None}
        reserves = multicall_same_func_no_input(deepest_pool_by_router.values(), 'getReserves()((uint112,uint112,uint32))', block=block)
        routers_by_depth = {}
        for router, pool, reserves in zip(deepest_pool_by_router.keys(), deepest_pool_by_router.values(), reserves):
            if reserves is None: continue
            if token_in == router.pools[pool]['token0']:
                routers_by_depth[reserves[0]] = router
            elif token_in == router.pools[pool]['token1']:
                routers_by_depth[reserves[1]] = router
        return {
            routers_by_depth[balance]: deepest_pool_by_router[routers_by_depth[balance]]
            for balance in sorted(routers_by_depth.keys(), reverse=True)
        }


uniswap = Uniswap()
