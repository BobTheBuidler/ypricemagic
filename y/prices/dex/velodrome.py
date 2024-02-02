import asyncio
import logging
from typing import List, Optional, Set, Tuple

import a_sync
from async_lru import alru_cache
from brownie import chain
from multicall.call import Call

from y import ENVIRONMENT_VARIABLES as ENVS
from y.contracts import Contract
from y.datatypes import Address, AnyAddressType, Block
from y.decorators import stuck_coro_debugger
from y.interfaces.uniswap.velov2 import VELO_V2_FACTORY_ABI
from y.networks import Network
from y.prices.dex.solidly import SolidlyRouterBase
from y.prices.dex.uniswap.v2 import Path, UniswapV2Pool
from y.utils import gather_methods
from y.utils.dank_mids import dank_w3
from y.utils.raw_calls import raw_call

_INIT_METHODS = 'token0()(address)', 'token1()(address)', 'stable()(bool)'

logger = logging.getLogger(__name__)

class NoReservesError(Exception):
    pass

default_factory = {
    Network.Optimism: "0xF1046053aa5682b4F9a81b5481394DA16BE5FF5a",
    Network.Base: "0x420DD381b31aEf6683db6B902084cB0FFECe40Da",
}

class VelodromePool(UniswapV2Pool):
    __slots__ = "is_stable", 
    def __init__(
        self, 
        address: AnyAddressType, 
        token0: Optional[AnyAddressType] = None, 
        token1: Optional[AnyAddressType] = None,
        stable: Optional[bool] = None,
        deploy_block: Optional[int] = None,
        asynchronous: bool = False,
    ):
        super().__init__(address, token0=token0, token1=token1, deploy_block=deploy_block, asynchronous=asynchronous)
        self.is_stable = stable

class VelodromeRouterV2(SolidlyRouterBase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.default_factory = default_factory[chain.id]
    
    @stuck_coro_debugger
    @a_sync.a_sync(ram_cache_ttl=ENVS.CACHE_TTL)
    async def pool_for(self, input_token: Address, output_token: Address, stable: bool) -> Address:
        return await self.contract.poolFor.coroutine(input_token, output_token, stable, self.default_factory)
    
    @stuck_coro_debugger
    @a_sync.a_sync(ram_cache_ttl=ENVS.CACHE_TTL)
    async def get_pool(self, input_token: Address, output_token: Address, stable: bool, block: Block) -> Optional[UniswapV2Pool]:
        pool_address = await self.pool_for(input_token, output_token, stable, sync=False)
        if await dank_w3.eth.get_code(str(pool_address), block_identifier=block) not in ['0x',b'']:
            return UniswapV2Pool(pool_address, asynchronous=self.asynchronous)
    
    @a_sync.aka.cached_property
    @stuck_coro_debugger
    async def pools(self) -> Set[UniswapV2Pool]:
        logger.info('Fetching pools for %s on %s. If this is your first time using ypricemagic, this can take a while. Please wait patiently...', self.label, Network.printable())
        factory = await Contract.coroutine(self.factory)
        if 'PoolCreated' not in factory.topics:
            # the etherscan proxy detection is borked here, need this to decode properly
            factory = Contract.from_abi("PoolFactory", self.factory, VELO_V2_FACTORY_ABI)

        try:
            pools = {
                VelodromePool(
                    address=event['pool'],
                    token0=event['token0'], 
                    token1=event['token1'], 
                    stable=event['stable'], 
                    deploy_block=event.block_number, 
                    asynchronous=self.asynchronous,
                )
                async for event in factory.events.PoolCreated.events(to_block=await dank_w3.eth.block_number)
            }
        except Exception as e:
            print(e)
            raise e
        
        all_pools_len = await raw_call(self.factory, 'allPoolsLength()', block=chain.height, output='int', sync=False)

        if len(pools) > all_pools_len:
            raise ValueError('wtf', len(pools), all_pools_len)
        
        if len(pools) < all_pools_len:
            logger.debug("Oh no! Looks like your node can't look back that far. Checking for the missing %s pools...", all_pools_len - len(pools))
            pools_your_node_couldnt_get = {
                i: asyncio.create_task(coro=self._init_pool_from_poolid(i), name=f"load {self} poolId {i}") 
                for i in range(all_pools_len - len(pools))
            }
            logger.debug('pools: %s', pools_your_node_couldnt_get)
            pools.update([pool async for id, pool in a_sync.as_completed(pools_your_node_couldnt_get, aiter=True)])

        tokens = set()
        for pool in pools:
            tokens.update(await asyncio.gather(pool.__token0__(sync=False), pool.__token1__(sync=False)))
        logger.info('Loaded %s pools supporting %s tokens on %s', len(pools), len(tokens), self.label)
        return pools
    
    @stuck_coro_debugger
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
                    stable_pool.reserves(block=block, sync=False),
                    unstable_pool.reserves(block=block, sync=False),
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

    @stuck_coro_debugger
    async def _init_pool_from_poolid(self, poolid: int) -> VelodromePool:
        logger.debug("initing poolid %s", poolid)
        pool = await Call(self.factory, ['allPools(uint256)(address)']).coroutine(poolid)
        if pool is None: # TODO: debug why this happens sometimes
            factory = await Contract.coroutine(self.factory)
            pool = await factory.allPools(poolid)
        token0, token1, stable = await gather_methods(pool, _INIT_METHODS)
        return VelodromePool(
            address=pool,
            token0=token0,
            token1=token1, 
            stable=stable, 
            asynchronous=self.asynchronous,
        )


_get_code = alru_cache(maxsize=None)(dank_w3.eth.get_code)
