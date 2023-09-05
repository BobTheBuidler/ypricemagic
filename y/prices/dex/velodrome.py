import asyncio
import logging
from collections import defaultdict
from typing import DefaultDict, Dict, List, Optional, Tuple

import a_sync
from async_lru import alru_cache
from brownie import chain
from multicall.call import Call

from y import ENVIRONMENT_VARIABLES as ENVS
from y import convert
from y.classes.common import _ObjectStream
from y.contracts import Contract
from y.datatypes import Address, Block
from y.interfaces.uniswap.velov2 import VELO_V2_FACTORY_ABI
from y.networks import Network
from y.prices.dex.solidly import SolidlyRouterBase
from y.prices.dex.uniswap.v2 import Path, UniswapV2Pool
from y.utils.dank_mids import dank_w3
from y.utils.events import EventStream, decode_logs, get_logs_asap
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)


class NoReservesError(Exception):
    pass

default_factory = {
    Network.Optimism: "0xF1046053aa5682b4F9a81b5481394DA16BE5FF5a",
    Network.Base: "0x420DD381b31aEf6683db6B902084cB0FFECe40Da",
}

class VelodromeRouterV2(SolidlyRouterBase):
    def __init__(self, router_address: Address, *args, **kwargs):
        super().__init__(router_address, *args, **kwargs)
        self.default_factory = default_factory[chain.id]
    
    @a_sync.a_sync(ram_cache_ttl=ENVS.CACHE_TTL)
    async def pool_for(self, input_token: Address, output_token: Address, stable: bool) -> Address:
        return await self.contract.poolFor.coroutine(input_token, output_token, stable, self.default_factory)
    
    @a_sync.a_sync(ram_cache_ttl=ENVS.CACHE_TTL)
    async def get_pool(self, input_token: Address, output_token: Address, stable: bool, block: Block) -> Optional[UniswapV2Pool]:
        pool_address = await self.pool_for(input_token, output_token, stable, sync=False)
        if await dank_w3.eth.get_code(str(pool_address), block_identifier=block) not in ['0x',b'']:
            return UniswapV2Pool(pool_address, asynchronous=self.asynchronous)

    async def get_routes_from_path(self, path: Path, block: Block) -> List[Tuple[Address, Address, bool]]:
        routes = []
        for i in range(len(path) - 1):
            input_token, output_token = path[i], path[i+1]
            # Try for a stable pool first and use that if available
            stable_pool, unstable_pool = await asyncio.gather(
                self.get_pool(input_token, output_token, True, block, sync=False),
                self.get_pool(input_token, output_token, False, block, sync=False),
            )
            
            if stable_pool and unstable_pool:
                # We have to find out which of these pools is deepest
                stable_reserves, unstable_reserves = await asyncio.gather(
                    stable_pool.reserves(block, sync=False),
                    unstable_pool.reserves(block, sync=False),
                )
                if stable_reserves and unstable_reserves:
                    stable_reserves = tuple(stable_reserves)
                    unstable_reserves = tuple(unstable_reserves)
                    if await stable_pool.__tokens__(sync=False) == await unstable_pool.__tokens__(sync=False):
                        stable_reserve = stable_reserves[0]
                        unstable_reserve = unstable_reserves[0]
                    else:  # Order of tokens is flip flopped in the pools
                        stable_reserve = stable_reserves[0]
                        unstable_reserve = unstable_reserves[1]
                    if stable_reserve >= unstable_reserve:
                        is_stable = True
                    elif stable_reserve < unstable_reserve:
                        is_stable = False
                    routes.append([input_token, output_token, is_stable, self.factory])
                elif stable_reserves:
                    routes.append([input_token, output_token, True, self.factory])
                elif unstable_reserves:
                    routes.append([input_token, output_token, False, self.factory])
                else:
                    raise NoReservesError(f"No route available for path {path}")
            elif stable_pool:
                routes.append([input_token, output_token, True, self.factory])
            elif unstable_pool:
                routes.append([input_token, output_token, False, self.factory])
            else:
                raise ValueError("Not sure why this function is even running if no pool is found")
            
        return routes


class Pools(_ObjectStream[UniswapV2Pool]):
    def __init__(self, factory: Address, asynchronous: bool, run_forever: bool = True) -> None:
        super().__init__(run_forever=run_forever)
        self.asynchronous = asynchronous
        self.factory = factory
    
    @property
    def _pools(self) -> DefaultDict[int, List[UniswapV2Pool]]:
        return self._objects
    
    async def _fetcher_task(self):
        last_block = 0
        factory = await Contract.coroutine(self.factory)
        if 'PoolCreated' not in factory.topics:
            # the etherscan proxy detection is borked here, need this to decode properly
            factory = Contract.from_abi("PoolFactory", self.factory, VELO_V2_FACTORY_ABI)
        async for event in EventStream(factory, [factory.topics['PoolCreated']], run_forever=self.run_forever):
            block = event.block_number
            if block > last_block:
                self._block = last_block
            # NOTE: we should probably subclass univ2 pool and use this for init
            stable = event['stable']
            pool = UniswapV2Pool(
                address=event['pool'], 
                token0=event['token0'], 
                token1=event['token1'], 
                asynchronous=self.asynchronous,
            )
            self._pools[block].append(pool)
            last_block = block
            self._read.set()
            self._read.clear()