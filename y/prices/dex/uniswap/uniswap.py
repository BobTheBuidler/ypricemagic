import asyncio
import logging
import os
import threading
from typing import Dict, Optional, Union, List

import a_sync
from brownie import ZERO_ADDRESS, chain

from y import convert
from y.classes.common import ERC20
from y.datatypes import Address, AnyAddressType, Block, UsdPrice
from y.exceptions import NonStandardERC20, contract_not_verified
from y.networks import Network
from y.prices.dex.solidly import SolidlyRouter
from y.prices.dex.uniswap.v1 import UniswapV1
from y.prices.dex.uniswap.v2 import (NotAUniswapV2Pool, UniswapV2Pool,
                                     UniswapRouterV2)
from y.prices.dex.uniswap.v2_forks import UNISWAPS
from y.prices.dex.uniswap.v3 import UniswapV3, uniswap_v3
from y.prices.dex.velodrome import VelodromeRouterV2
from y.utils.logging import _gh_issue_request

logger = logging.getLogger(__name__)

# NOTE: If this is failing to pull a price for a token you need, it's likely because that token requires a special swap path.
#       Please add a viable swap path to ..protocols to fetch price data successfully.

_special_routers = {
    "solidly": SolidlyRouter,
    "velodrome v1": SolidlyRouter,
    "velodrome v2": VelodromeRouterV2,
}

Uniswap = Union[UniswapV1, UniswapRouterV2, UniswapV3]

class UniswapMultiplexer(a_sync.ASyncGenericSingleton):
    def __init__(self, asynchronous: bool = False) -> None:
        self.asynchronous = asynchronous
        self.v2_routers = {}
        for name in UNISWAPS:
            router_cls = _special_routers.get(name, UniswapRouterV2)
            try: self.v2_routers[name] = router_cls(UNISWAPS[name]['router'], asynchronous=self.asynchronous)
            except ValueError as e: # TODO do this better
                if not contract_not_verified(e):
                    raise
        self.v1 = UniswapV1(asynchronous=self.asynchronous) if chain.id == Network.Mainnet else None
        self.v3 = UniswapV3(asynchronous=self.asynchronous) if uniswap_v3 else None

        self.uniswaps: List[Uniswap] = []
        if self.v1:
            self.uniswaps.append(self.v1)
        self.uniswaps.extend(self.v2_routers.values())
        if self.v3:
            self.uniswaps.append(self.v3)

        self.v2_factories = [UNISWAPS[name]['factory'] for name in UNISWAPS]
        self._uid_lock = threading.Lock()

    async def is_uniswap_pool(self, token_address: AnyAddressType) -> bool:
        token_address = convert.to_address(token_address)
        try:
            await ERC20(token_address, asynchronous=True).decimals
        except NonStandardERC20:
            return False
        try:
            pool = UniswapV2Pool(token_address, asynchronous=True)
            is_pool = all(await pool.get_pool_details(sync=False))
            if is_pool:
                factory = await pool.__factory__(sync=False)
                if factory not in self.v2_factories and factory != ZERO_ADDRESS:
                    _gh_issue_request(f'UniClone Factory {factory} is unknown to ypricemagic.', logger)
                    self.v2_factories.append(factory)
            return is_pool
        except NotAUniswapV2Pool:
            return False

    async def get_price(self, token_in: AnyAddressType, block: Optional[Block] = None) -> Optional[UsdPrice]:
        """
        Calculate a price based on Uniswap Router quote for selling one `token_in`.
        Always finds the deepest swap path for `token_in`.
        """
        router: Uniswap
        token_in = convert.to_address(token_in)
        for router in await self.routers_by_depth(token_in, block=block, sync=False):
            # tries each known router from most to least liquid
            # returns the first price we get back, almost always from the deepest router
            price = await router.get_price(token_in, block=block, sync=False)
            logger.debug("%s -> %s", router, price)
            if price:
                return price
    
    """ lets make sure we can delete this
    # NOTE: This uses mad memory so we arbitrarily cut it off at 50.
    #       Feel free to implement your own limit with the env var. 
    @a_sync.a_sync(semaphore=int(os.environ.get("YPM_DEEPEST_ROUTER_SEMAPHORE", 50)))
    async def deepest_router(self, token_in: AnyAddressType, block: Optional[Block] = None) -> Optional[Uniswap]:
        token_in = convert.to_address(token_in)
        deepest_router = None
        deepest_router_depth = 0
        for router, depth in zip(self.uniswaps, await asyncio.gather(*[uniswap.check_liquidity(token_in, block, sync=False) for uniswap in self.uniswaps])):
            if depth > deepest_router_depth:
                deepest_router = router
                deepest_router_depth = depth
        return deepest_router
    """

    async def routers_by_depth(self, token_in: AnyAddressType, block: Optional[Block] = None) -> Dict[UniswapRouterV2,str]:
        '''
        Returns a dict {router: pool} ordered by liquidity depth, greatest to least
        '''
        token_in = convert.to_address(token_in)
        depth_to_router = dict(zip(await asyncio.gather(*[uniswap.check_liquidity(token_in, block, sync=False) for uniswap in self.uniswaps]), routers))
        return {router: pool for balance in sorted(depth_to_router, reverse=True) for router, pool in depth_to_router[balance].items()}
    
    async def check_liquidity(self, token: Address, block: Block) -> int:
        return max(await asyncio.gather(*[uniswap.check_liquidity(token, block, sync=False) for uniswap in self.uniswaps]))


uniswap_multiplexer = UniswapMultiplexer(asynchronous=True)
