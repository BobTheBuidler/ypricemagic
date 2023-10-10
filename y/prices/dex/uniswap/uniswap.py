import asyncio
import logging
import threading
from contextlib import suppress
from typing import List, Optional, Tuple, Union

import a_sync
from brownie import ZERO_ADDRESS, chain
from web3.exceptions import ContractLogicError

from y import convert
from y.classes.common import ERC20
from y.datatypes import Address, AnyAddressType, Block, Pool, UsdPrice
from y.decorators import stuck_coro_debugger
from y.exceptions import NonStandardERC20, contract_not_verified
from y.networks import Network
from y.prices.dex.solidly import SolidlyRouter
from y.prices.dex.uniswap.v1 import UniswapV1
from y.prices.dex.uniswap.v2 import (NotAUniswapV2Pool, UniswapRouterV2,
                                     UniswapV2Pool)
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
    "aerodrome": VelodromeRouterV2,
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

    @stuck_coro_debugger
    async def is_uniswap_pool(self, token_address: AnyAddressType) -> bool:
        token_address = convert.to_address(token_address)
        try:
            await ERC20(token_address, asynchronous=True).decimals
        except NonStandardERC20:
            return False
    
        pool = UniswapV2Pool(token_address, asynchronous=True)
        with suppress(NotAUniswapV2Pool, ContractLogicError):
            if await pool.is_uniswap_pool(sync=False):
                factory = await pool.__factory__(sync=False)
                if factory not in self.v2_factories and factory != ZERO_ADDRESS:
                    _gh_issue_request(f'UniClone Factory {factory} is unknown to ypricemagic.', logger)
                    self.v2_factories.append(factory)
                return True
        return False

    @stuck_coro_debugger
    async def get_price(
        self, 
        token_in: AnyAddressType, 
        block: Optional[Block] = None, 
        ignore_pools: Tuple[Pool, ...] = (),
    ) -> Optional[UsdPrice]:
        """
        Calculate a price based on Uniswap Router quote for selling one `token_in`.
        Always finds the deepest swap path for `token_in`.
        """
        router: Uniswap
        token_in = convert.to_address(token_in)
        for router in await self.routers_by_depth(token_in, block=block, ignore_pools=ignore_pools, sync=False):
            # tries each known router from most to least liquid
            # returns the first price we get back, almost always from the deepest router
            price = await router.get_price(token_in, block=block, ignore_pools=ignore_pools, sync=False)
            logger.debug("%s -> %s", router, price)
            if price:
                return price

    @stuck_coro_debugger
    async def routers_by_depth(
        self, 
        token_in: AnyAddressType, 
        block: Optional[Block] = None, 
        ignore_pools: Tuple[Pool, ...] = (),
    ) -> List[UniswapRouterV2]:
        '''
        Returns a dict {router: pool} ordered by liquidity depth, greatest to least
        '''
        token_in = convert.to_address(token_in)
        depth_to_router = dict(zip(await asyncio.gather(*[uniswap.check_liquidity(token_in, block, ignore_pools=ignore_pools, sync=False) for uniswap in self.uniswaps]), self.uniswaps))
        return [depth_to_router[balance] for balance in sorted(depth_to_router, reverse=True) if balance]
    
    @stuck_coro_debugger
    async def check_liquidity(
        self, 
        token: Address, 
        block: Block, 
        ignore_pools: Tuple[Pool, ...] = (),
    ) -> int:
        return max(await asyncio.gather(*[uniswap.check_liquidity(token, block, ignore_pools=ignore_pools, sync=False) for uniswap in self.uniswaps]))


uniswap_multiplexer = UniswapMultiplexer(asynchronous=True)
