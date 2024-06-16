import asyncio
import logging
from typing import List, Optional, Set, Tuple

import a_sync
import dank_mids
import eth_retry
from a_sync.a_sync.property import HiddenMethodDescriptor
from brownie import chain
from multicall.call import Call
from typing_extensions import Self

from y._decorators import stuck_coro_debugger
from y.contracts import Contract, contract_creation_block_async
from y.datatypes import Address, AnyAddressType, Block
from y.interfaces.uniswap.velov2 import VELO_V2_FACTORY_ABI
from y.networks import Network
from y.prices.dex.solidly import SolidlyRouterBase
from y.prices.dex.uniswap.v2 import Path, UniswapV2Pool
from y.utils import gather_methods
from y.utils.cache import a_sync_ttl_cache
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
    _supports_uniswap_helper = False
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.default_factory = default_factory[chain.id]
    
    @stuck_coro_debugger
    @a_sync_ttl_cache
    async def pool_for(self, input_token: Address, output_token: Address, stable: bool) -> Optional[Address]:
        pool_address = str(await self.contract.poolFor.coroutine(input_token, output_token, stable, self.default_factory))
        if await is_contract(pool_address):
            return pool_address
    
    @stuck_coro_debugger
    @a_sync_ttl_cache
    @eth_retry.auto_retry
    async def get_pool(self, input_token: Address, output_token: Address, stable: bool, block: Block) -> Optional[UniswapV2Pool]:
        if pool_address := await self.pool_for(input_token, output_token, stable, sync=False):
            if await contract_creation_block_async(pool_address) <= block:
                return UniswapV2Pool(pool_address, asynchronous=self.asynchronous)
    
    @a_sync.aka.cached_property
    @stuck_coro_debugger
    async def pools(self) -> Set[VelodromePool]:
        logger.info('Fetching pools for %s on %s. If this is your first time using ypricemagic, this can take a while. Please wait patiently...', self.label, Network.printable())
        factory = await Contract.coroutine(self.factory)
        if 'PoolCreated' not in factory.topics:
            # the etherscan proxy detection is borked here, need this to decode properly
            factory = Contract.from_abi("PoolFactory", self.factory, VELO_V2_FACTORY_ABI)

        pools = {
            VelodromePool(
                address=event['pool'],
                token0=event['token0'], 
                token1=event['token1'], 
                stable=event['stable'], 
                deploy_block=event.block_number, 
                asynchronous=self.asynchronous,
            )
            async for event in factory.events.PoolCreated.events(to_block=await dank_mids.eth.block_number)
        }
        
        all_pools_len = await raw_call(self.factory, 'allPoolsLength()', output='int', sync=False)

        if len(pools) > all_pools_len:
            raise ValueError('wtf', len(pools), all_pools_len)
        
        if len(pools) < all_pools_len:
            logger.debug("Oh no! Looks like your node can't look back that far. Checking for the missing %s pools...", all_pools_len - len(pools))
            pools_your_node_couldnt_get = a_sync.map(self._init_pool_from_poolid, range(all_pools_len - len(pools)), name=f"load {self} poolId")
            # we want the map populated with tasks for this logger
            await pools_your_node_couldnt_get._init_loader
            logger.debug('pools: %s', pools_your_node_couldnt_get)
            pools.update(await pools_your_node_couldnt_get.values(pop=True))

        tokens = set()
        for pool in pools:
            tokens.update(await asyncio.gather(pool.__token0__, pool.__token1__))
        logger.info('Loaded %s pools supporting %s tokens on %s', len(pools), len(tokens), self.label)
        return pools
    __pools__: HiddenMethodDescriptor[Self, Set[VelodromePool]]
    
    @stuck_coro_debugger
    async def get_routes_from_path(self, path: Path, block: Block) -> List[Tuple[Address, Address, bool]]:
        routes = []
        for i in range(len(path) - 1):
            input_token, output_token = path[i], path[i+1]
            # Try for a stable pool first and use that if available
            stable_pool: Optional[VelodromePool]
            unstable_pool: Optional[VelodromePool]
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

                    # NOTE: using `__token0__` and `__token1__` is faster than `__tokens__` since they're already cached and return instantly
                    #       it also creates 2 fewer tasks and 1 fewer future than `__tokens__` since there is no use of `asyncio.gather`.
                    if await stable_pool.__token0__ == await unstable_pool.__token0__ and await stable_pool.__token1__ == await unstable_pool.__token1__:
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
        if pool is None:  # TODO: debug why this happens sometimes and why this if clause works to get back on track
            factory = await Contract.coroutine(self.factory)
            pool = await factory.allPools.coroutine(poolid)
        token0, token1, stable = await gather_methods(pool, _INIT_METHODS)
        return VelodromePool(
            address=pool,
            token0=token0,
            token1=token1, 
            stable=stable, 
            asynchronous=self.asynchronous,
        )


async def is_contract(pool_address: Address) -> bool:
    if pool_address in __pools:
        return True
    if result := await dank_mids.eth.get_code(pool_address) not in ['0x',b'']:
        __pools.append(pool_address)
    return result

__pools = []