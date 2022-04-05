import logging
from typing import Dict, Optional

from brownie import chain
from cachetools.func import ttl_cache
from y import convert
from y.datatypes import UsdPrice
from y.decorators import log
from y.exceptions import contract_not_verified
from y.networks import Network
from y.prices.dex.uniswap.v1 import UniswapV1
from y.prices.dex.uniswap.v2 import (NotAUniswapV2Pool, UniswapPoolV2,
                                     UniswapRouterV2)
from y.prices.dex.uniswap.v2_forks import UNISWAPS
from y.typing import Address, AnyAddressType, Block
from y.utils.logging import gh_issue_request
from y.utils.multicall import multicall_same_func_no_input

logger = logging.getLogger(__name__)

# NOTE: If this is failing to pull a price for a token you need, it's likely because that token requires a special swap path.
#       Please add a viable swap path to ..protocols to fetch price data successfully.

class UniswapMultiplexer:
    def __init__(self) -> None:
        self.routers = {}
        for name in UNISWAPS:
            try: self.routers[name] = UniswapRouterV2(UNISWAPS[name]['router'])
            except ValueError as e: # TODO do this better
                if not contract_not_verified(e):
                    raise
        self.factories = [UNISWAPS[name]['factory'] for name in UNISWAPS]
        self.v1 = UniswapV1()

    @log(logger)
    def is_uniswap_pool(self, token_address: AnyAddressType) -> bool:
        token_address = convert.to_address(token_address)
        try:
            pool = UniswapPoolV2(token_address)
            is_pool = all(pool.get_pool_details())
            if is_pool and pool.factory not in self.factories:
                gh_issue_request(f'UniClone Factory {pool.factory} is unknown to ypricemagic.', logger)
                self.factories.append(pool.factory)
            return is_pool

        except NotAUniswapV2Pool: return False

    @log(logger)
    def get_price_v1(self, token_address: Address, block: Optional[Block] = None) -> UsdPrice:
        return self.v1.get_price(token_address, block)
    
    @log(logger)
    @ttl_cache(ttl=600)
    def lp_price(self, token_address: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
        """ Get Uniswap/Sushiswap LP token price. """
        return UniswapPoolV2(token_address).get_price(block=block)
    
    @log(logger)
    @ttl_cache(ttl=36000)
    def get_price(self, token_in: AnyAddressType, block: Optional[Block] = None, protocol: Optional[str] = None) -> Optional[UsdPrice]:
        """
        Calculate a price based on Uniswap Router quote for selling one `token_in`.
        Always finds the deepest swap path for `token_in`.
        """
        token_in = convert.to_address(token_in)

        if protocol:
            return self.routers[protocol].get_price(token_in, block=block)

        for router in self.routers_by_depth(token_in, block=block):
            # tries each known router from most to least liquid
            # returns the first price we get back, almost always from the deepest router
            price = router.get_price(token_in, block=block)
            if price:
                return price
        
        if chain.id == Network.Mainnet:
            return self.get_price_v1(token_in, block)
        
        return None
    

    @log(logger)
    def deepest_router(self, token_in: AnyAddressType, block: Optional[Block] = None) -> Optional[UniswapRouterV2]:
        token_in = convert.to_address(token_in)

        for router in self.routers_by_depth(token_in, block=block):
            return router # will return first router in the dict, or None if no supported routers
        return None


    @log(logger)
    def routers_by_depth(self, token_in: AnyAddressType, block: Optional[Block] = None) -> Dict[UniswapRouterV2,str]:
        '''
        Returns a dict {router: pool} ordered by liquidity depth, greatest to least
        '''
        token_in = convert.to_address(token_in)

        pools_to_routers = {pool: router for router in self.routers.values() for pool in router.pools_for_token(token_in)}
        reserves = multicall_same_func_no_input(pools_to_routers, 'getReserves()((uint112,uint112,uint32))', block=block, return_None_on_failure=True)
        routers_by_depth = {}
        for router, pool, reserves in zip(pools_to_routers.values(), pools_to_routers.keys(), reserves):
            if reserves is None:
                continue
            if token_in == router.pools[pool]['token0']:
                routers_by_depth[reserves[0]] = {router: pool}
            elif token_in == router.pools[pool]['token1']:
                routers_by_depth[reserves[1]] = {router: pool}
        return {router: pool for balance in sorted(routers_by_depth, reverse=True) for router, pool in routers_by_depth[balance].items()}


uniswap_multiplexer = UniswapMultiplexer()
