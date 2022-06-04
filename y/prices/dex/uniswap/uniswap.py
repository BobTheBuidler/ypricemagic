import logging
import os
import threading
from typing import Dict, List, Optional, Tuple

from async_lru import alru_cache
from brownie import chain
from cachetools.func import ttl_cache
from joblib import Parallel, delayed
from multicall import Call, Multicall
from multicall.utils import await_awaitable, gather
from y import convert
from y.datatypes import Address, AnyAddressType, Block, UsdPrice
from y.exceptions import contract_not_verified
from y.networks import Network
from y.prices.dex.uniswap.v1 import UniswapV1
from y.prices.dex.uniswap.v2 import (NotAUniswapV2Pool, UniswapPoolV2,
                                     UniswapRouterV2)
from y.prices.dex.uniswap.v2_forks import UNISWAPS
from y.utils.logging import gh_issue_request, yLazyLogger

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
        self._uid_lock = threading.Lock()

    @yLazyLogger(logger)
    def is_uniswap_pool(self, token_address: AnyAddressType) -> bool:
        return await_awaitable(self.is_uniswap_pool_async(token_address))

    @yLazyLogger(logger)
    async def is_uniswap_pool_async(self, token_address: AnyAddressType) -> bool:
        token_address = convert.to_address(token_address)
        try:
            pool = UniswapPoolV2(token_address)
            is_pool = all(await pool.get_pool_details_async())
            if is_pool:
                factory = await pool.factory_async
                if factory not in self.factories:
                    gh_issue_request(f'UniClone Factory {pool.factory} is unknown to ypricemagic.', logger)
                    self.factories.append(pool.factory)
            return is_pool

        except NotAUniswapV2Pool: return False

    @yLazyLogger(logger)
    def get_price_v1(self, token_address: Address, block: Optional[Block] = None) -> UsdPrice:
        return await_awaitable(self.get_price_v1_async(token_address, block=block))
    
    @yLazyLogger(logger)
    async def get_price_v1_async(self, token_address: Address, block: Optional[Block] = None) -> UsdPrice:
        return await self.v1.get_price_async(token_address, block)
    
    @yLazyLogger(logger)
    @ttl_cache(ttl=600)
    def lp_price(self, token_address: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
        """ Get Uniswap/Sushiswap LP token price. """
        return await_awaitable(self.lp_price_async(token_address, block=block))
    
    @yLazyLogger(logger)
    @alru_cache(maxsize=500)
    async def lp_price_async(self, token_address: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
        """ Get Uniswap/Sushiswap LP token price. """
        return await UniswapPoolV2(token_address).get_price_async(block=block)
    
    @yLazyLogger(logger)
    @ttl_cache(ttl=36000)
    def get_price(self, token_in: AnyAddressType, block: Optional[Block] = None, protocol: Optional[str] = None) -> Optional[UsdPrice]:
        return await_awaitable(self.get_price_async(token_in, block=block, protocol=protocol))
    
    @yLazyLogger(logger)
    async def get_price_async(self, token_in: AnyAddressType, block: Optional[Block] = None, protocol: Optional[str] = None) -> Optional[UsdPrice]:
        """
        Calculate a price based on Uniswap Router quote for selling one `token_in`.
        Always finds the deepest swap path for `token_in`.
        """
        token_in = convert.to_address(token_in)

        if protocol:
            return await self.routers[protocol].get_price_async(token_in, block=block)

        for router in await self.routers_by_depth_async(token_in, block=block):
            # tries each known router from most to least liquid
            # returns the first price we get back, almost always from the deepest router
            price = await router.get_price_async(token_in, block=block)
            if price:
                return price
        
        if chain.id == Network.Mainnet:
            return await self.get_price_v1_async(token_in, block)
        
        return None
    
    @yLazyLogger(logger)
    def deepest_router(self, token_in: AnyAddressType, block: Optional[Block] = None) -> Optional[UniswapRouterV2]:
        return await_awaitable(self.deepest_router_async(token_in, block=block))
    
    @yLazyLogger(logger)
    async def deepest_router_async(self, token_in: AnyAddressType, block: Optional[Block] = None) -> Optional[UniswapRouterV2]:
        token_in = convert.to_address(token_in)

        for router in await self.routers_by_depth_async(token_in, block=block):
            return router # will return first router in the dict, or None if no supported routers
        return None

    @yLazyLogger(logger)
    def routers_by_depth(self, token_in: AnyAddressType, block: Optional[Block] = None) -> Dict[UniswapRouterV2,str]:
        return await_awaitable(self.routers_by_depth_async(token_in, block=block))

    @yLazyLogger(logger)
    async def routers_by_depth_async(self, token_in: AnyAddressType, block: Optional[Block] = None) -> Dict[UniswapRouterV2,str]:
        '''
        Returns a dict {router: pool} ordered by liquidity depth, greatest to least
        '''
        calls = await self._routers_by_depth_calls_async(token_in)
        reserves = (await Multicall(calls, block_id=block, require_success=False).coroutine()).values()
        return await self._routers_by_depth_logic_async(token_in, reserves)


    def _routers_by_depth_calls(self, token_in: AnyAddressType) -> List[Call]:
        ''' Returns List[Calls] to use for multicall and bool to indicate whether to require success on the multicall. '''
        return await_awaitable(self._routers_by_depth_calls_async(token_in))
    
    async def _routers_by_depth_calls_async(self, token_in: AnyAddressType) -> List[Call]:
        ''' Returns List[Calls] to use for multicall and bool to indicate whether to require success on the multicall. '''
        token_in = convert.to_address(token_in)
        routers = self.routers.values()
        pools_per_router = await gather([router.pools_for_token_async(token_in) for router in routers])
        pools_to_routers = {pool: router for router, pools in zip(routers,pools_per_router) for pool in pools}
        return [Call(pool, 'getReserves()((uint112,uint112,uint32))', [[self._next_uid(), None]]) for pool in pools_to_routers]
    

    def _routers_by_depth_logic(self, token_in: AnyAddressType, getReserves_call_responses: List[Tuple[int,int,int]]) -> Dict[UniswapRouterV2, str]:
        return await_awaitable(self._routers_by_depth_logic_async(token_in, getReserves_call_responses))
    
    async def _routers_by_depth_logic_async(self, token_in: AnyAddressType, getReserves_call_responses: List[Tuple[int,int,int]]) -> Dict[UniswapRouterV2, str]:
        ''' uses the results of a multicall built by `_routers_by_debth_calls` to output routers_by_depth. '''
        routers = self.routers.values()
        pools = await gather([router.pools_for_token_async(token_in) for router in routers])

        pools_to_routers = {
            pool: router
            for router, pools in zip(routers, pools)
            for pool in pools
        }

        routers_by_depth = {}
        for router, pool, reserves in zip(pools_to_routers.values(), pools_to_routers.keys(), getReserves_call_responses):
            if reserves is None:
                continue
            if token_in == (await router.pools_async)[pool]['token0']:
                routers_by_depth[reserves[0]] = {router: pool}
            elif token_in == (await router.pools_async)[pool]['token1']:
                routers_by_depth[reserves[1]] = {router: pool}
        return {router: pool for balance in sorted(routers_by_depth, reverse=True) for router, pool in routers_by_depth[balance].items()}

    def _next_uid(self) -> str:
        with self._uid_lock:
            try:
                self._last_uid += 1
            except AttributeError:
                self._last_uid = 0
            return f"call_{self._last_uid}"

    def _get_prices(
        self,
        token_addresses: List[AnyAddressType],
        block: Optional[Block] = None,
        dop: int = int(os.environ.get('DOP',4))
        ) -> List[Optional[UsdPrice]]:
        ''' Get uniswap prices for multiple tokens at once, optimized for speed. '''

        token_addresses = [convert.to_address(token) for token in token_addresses]
        if block is None:
            block = chain.height

        # First we collect calls so we can evaluate `routers_by_depth` efficiently using multicall, for minimal total calls.
        calls_dict = {
            i: self._routers_by_depth_calls(token_addresses[i])
            for i in range(len(token_addresses))
        }

        # Then we set up and execute the multicall.
        calls = [call for i, calls in calls_dict.items() for call in calls]
        responses = list(Multicall(calls, block_id=block, require_success=False)().values())
        assert len(calls) == len(responses), f"There is an issue with your multicall. Must investigate. len(calls): {len(calls)}  len(reserves): {len(responses)}"

        # Then we separate the results by input token and evaluate `routers_by_depth` logic with the results.
        routers_by_depth = {}
        done = 0
        for i, calls in calls_dict.items():
            start = done
            end = start + len(calls)
            reserves = responses[start:end]
            routers_by_depth[i] = self._routers_by_depth_logic(token_addresses[i],reserves)
            done = end

        # Get prices for any token that has one
        # TODO optimize this for speed
        prices = Parallel(dop, 'threading')(delayed(self._get_price_from_routers)(token_addresses[i], routers, block) for i, routers in routers_by_depth.items())
        assert len(token_addresses) == len(prices)
        
        return prices

    def _get_price_from_routers(self, token: AnyAddressType, routers: Dict[UniswapRouterV2,str], block: Optional[Block] = None) -> Optional[UsdPrice]:
        token = convert.to_address(token)
        for router in routers:
            price = router.get_price(token, block)
            if price:
                return price

uniswap_multiplexer = UniswapMultiplexer()
