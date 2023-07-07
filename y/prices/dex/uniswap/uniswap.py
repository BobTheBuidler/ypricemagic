import asyncio
import logging
import os
import threading
from typing import Dict, Optional

import a_sync
from brownie import ZERO_ADDRESS, chain
from multicall import Call

from y import convert
from y.classes.common import ERC20
from y.datatypes import Address, AnyAddressType, Block, UsdPrice
from y.exceptions import NonStandardERC20, contract_not_verified
from y.networks import Network
from y.prices.dex.uniswap.v1 import UniswapV1
from y.prices.dex.uniswap.v2 import (NotAUniswapV2Pool, UniswapPoolV2,
                                     UniswapRouterV2)
from y.prices.dex.uniswap.v2_forks import UNISWAPS
from y.prices.dex.velodrome import VelodromeRouterV1
from y.utils.logging import _gh_issue_request

logger = logging.getLogger(__name__)

# NOTE: If this is failing to pull a price for a token you need, it's likely because that token requires a special swap path.
#       Please add a viable swap path to ..protocols to fetch price data successfully.

class UniswapMultiplexer(a_sync.ASyncGenericSingleton):
    def __init__(self, asynchronous: bool = False) -> None:
        self.asynchronous = asynchronous
        self.routers = {}
        for name in UNISWAPS:
            router_cls = VelodromeRouterV1 if name == "velodrome v1" else UniswapRouterV2
            try: self.routers[name] = router_cls(UNISWAPS[name]['router'], asynchronous=self.asynchronous)
            except ValueError as e: # TODO do this better
                if not contract_not_verified(e):
                    raise
        self.factories = [UNISWAPS[name]['factory'] for name in UNISWAPS]
        self.v1 = UniswapV1(asynchronous=self.asynchronous)
        self._uid_lock = threading.Lock()

    async def is_uniswap_pool(self, token_address: AnyAddressType) -> bool:
        token_address = convert.to_address(token_address)
        try:
            # TODO debug why we need sync kwarg here
            await ERC20(token_address, asynchronous=True).decimals
        except NonStandardERC20:
            return False
        try:
            pool = UniswapPoolV2(token_address, asynchronous=True)
            is_pool = all(await pool.get_pool_details(sync=False))
            if is_pool:
                factory = await pool.__factory__(sync=False)
                if factory not in self.factories and factory != ZERO_ADDRESS:
                    _gh_issue_request(f'UniClone Factory {factory} is unknown to ypricemagic.', logger)
                    self.factories.append(factory)
            return is_pool
        except NotAUniswapV2Pool:
            return False

    async def get_price_v1(self, token_address: Address, block: Optional[Block] = None) -> UsdPrice:
        return await self.v1.get_price(token_address, block, sync=False)
    
    @a_sync.a_sync(ram_cache_maxsize=500)
    async def lp_price(self, token_address: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
        """ Get Uniswap/Sushiswap LP token price. """
        # TODO debug why we need sync kwarg here
        return await UniswapPoolV2(token_address, asynchronous=True).get_price(block=block, sync=False)
    
    async def get_price(self, token_in: AnyAddressType, block: Optional[Block] = None, protocol: Optional[str] = None) -> Optional[UsdPrice]:
        """
        Calculate a price based on Uniswap Router quote for selling one `token_in`.
        Always finds the deepest swap path for `token_in`.
        """
        token_in = convert.to_address(token_in)

        if protocol:
            return await self.routers[protocol].get_price(token_in, block=block, sync=False)

        for router in await self.routers_by_depth(token_in, block=block, sync=False):
            # tries each known router from most to least liquid
            # returns the first price we get back, almost always from the deepest router
            price = await router.get_price(token_in, block=block, sync=False)
            if price:
                return price
        
        if chain.id == Network.Mainnet:
            return await self.get_price_v1(token_in, block, sync=False)
        
        return None
    
    # NOTE: This uses mad memory so we arbitrarily cut it off at 50.
    #       Feel free to implement your own limit with the env var. 
    @a_sync.a_sync(semaphore=int(os.environ.get("YPM_DEEPEST_ROUTER_SEMAPHORE", 50)))
    async def deepest_router(self, token_in: AnyAddressType, block: Optional[Block] = None) -> Optional[UniswapRouterV2]:
        token_in = convert.to_address(token_in)

        for router in await self.routers_by_depth(token_in, block=block, sync=False):
            return router # will return first router in the dict, or None if no supported routers
        return None

    
    async def routers_by_depth(self, token_in: AnyAddressType, block: Optional[Block] = None) -> Dict[UniswapRouterV2,str]:
        '''
        Returns a dict {router: pool} ordered by liquidity depth, greatest to least
        '''
        token_in = convert.to_address(token_in)
        routers = self.routers.values()
        pools_per_router = await asyncio.gather(*[router.pools_for_token(token_in, sync=False) for router in routers])
        pools_to_routers = {pool: router for router, pools in zip(routers,pools_per_router) for pool in pools}
        reserves = await asyncio.gather(
            *(Call(pool, 'getReserves()((uint112,uint112,uint32))', block_id=block).coroutine() for pool in pools_to_routers),
            return_exceptions=True,
        )

        routers_by_depth = {}
        for router, pool, reserves in zip(pools_to_routers.values(), pools_to_routers.keys(), reserves):
            if reserves is None or isinstance(reserves, Exception):
                continue
            if token_in == (await router.__pools__(sync=False))[pool]['token0']:
                routers_by_depth[reserves[0]] = {router: pool}
            elif token_in == (await router.__pools__(sync=False))[pool]['token1']:
                routers_by_depth[reserves[1]] = {router: pool}
        return {router: pool for balance in sorted(routers_by_depth, reverse=True) for router, pool in routers_by_depth[balance].items()}

    def _get_price_from_routers(self, token: AnyAddressType, routers: Dict[UniswapRouterV2,str], block: Optional[Block] = None) -> Optional[UsdPrice]:
        token = convert.to_address(token)
        for router in routers:
            price = router.get_price(token, block)
            if price:
                return price

uniswap_multiplexer = UniswapMultiplexer(asynchronous=True)
