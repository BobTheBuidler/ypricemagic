import asyncio
import logging
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import a_sync
from async_lru import alru_cache
from brownie import chain
from multicall.call import Call

from y import ENVIRONMENT_VARIABLES as ENVS
from y import convert
from y.contracts import Contract
from y.datatypes import Address, Block
from y.interfaces.uniswap.velov2 import VELO_V2_FACTORY_ABI
from y.networks import Network
from y.prices.dex.solidly import SolidlyRouterBase
from y.prices.dex.uniswap.v2 import Path, UniswapV2Pool
from y.utils.dank_mids import dank_w3
from y.utils.events import decode_logs, get_logs_asap
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)


class NoReservesError(Exception):
    pass

default_factory = {
    Network.Optimism: "0xF1046053aa5682b4F9a81b5481394DA16BE5FF5a",
    Network.Base: "0x420DD381b31aEf6683db6B902084cB0FFECe40Da",
}

class VelodromeRouterV2(SolidlyRouterBase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.default_factory = default_factory[chain.id]
    
    @a_sync.a_sync(ram_cache_ttl=ENVS.CACHE_TTL)
    async def pool_for(self, input_token: Address, output_token: Address, stable: bool) -> Address:
        return await self.contract.poolFor.coroutine(input_token, output_token, stable, self.default_factory)
    
    @a_sync.a_sync(ram_cache_ttl=ENVS.CACHE_TTL)
    async def get_pool(self, input_token: Address, output_token: Address, stable: bool, block: Block) -> Optional[UniswapV2Pool]:
        pool_address = await self.pool_for(input_token, output_token, stable, sync=False)
        if await dank_w3.eth.get_code(str(pool_address), block_identifier=block) not in ['0x',b'']:
            return UniswapV2Pool(pool_address, asynchronous=self.asynchronous)
    
    @a_sync.aka.cached_property
    async def pools(self) -> Dict[Address, Dict[Address,Address]]:
        logger.info('Fetching pools for %s on %s. If this is your first time using ypricemagic, this can take a while. Please wait patiently...', self.label, Network.printable())
        try:
            factory = await Contract.coroutine(self.factory)
            if 'PoolCreated' not in factory.topics:
                # the etherscan proxy detection is borked here, need this to decode properly
                factory = Contract.from_abi("PoolFactory", self.factory, VELO_V2_FACTORY_ABI)
            logs = await get_logs_asap(self.factory, [factory.topics['PoolCreated']], sync=False)
            pools = {
                convert.to_address(event['pool']): {
                    'token0': convert.to_address(event['token0']),
                    'token1': convert.to_address(event['token1']),
                    'stable': event['stable'],
                }
                for event in decode_logs(logs)
            }
        except Exception as e:
            print(e)
            raise e
        all_pairs_len = await raw_call(self.factory,'allPairsLength()',block=chain.height,output='int', sync=False)

        if len(pools) == all_pairs_len:
            return pools
        logger.debug("Oh no! Looks like your node can't look back that far. Checking for the missing %s pools...", all_pairs_len - len(pools))
        pools_your_node_couldnt_get = [i for i in range(all_pairs_len) if i not in range(len(pools))]
        logger.debug('pools: %s', pools_your_node_couldnt_get)
        pools_your_node_couldnt_get = await asyncio.gather(
            *[Call(self.factory, ['allPairs(uint256)(address)']).coroutine(i) for i in pools_your_node_couldnt_get]
        )
        token0s, token1s, stables = await asyncio.gather(
            asyncio.gather(*[Call(pool, ['token0()(address)']).coroutine() for pool in pools_your_node_couldnt_get]),
            asyncio.gather(*[Call(pool, ['token1()(address)']).coroutine() for pool in pools_your_node_couldnt_get]),
            asyncio.gather(*[Call(pool, ['stable()(bool)']).coroutine() for pool in pools_your_node_couldnt_get]),
        )
        pools_your_node_couldnt_get = {
            convert.to_address(pool): {
                'token0': convert.to_address(token0),
                'token1': convert.to_address(token1),
                'stable': stable
            }
            for pool, token0, token1, stable
            in zip(pools_your_node_couldnt_get, token0s, token1s, stables)
        }
        pools.update(pools_your_node_couldnt_get)

        tokens = set()
        for pool_params in pools.values():
            tokens.add(pool_params['token0'])
            tokens.add(pool_params['token1'])
        logger.info('Loaded %s pools supporting %s tokens on %s', len(pools), len(tokens), self.label)
        return pools
    
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


_get_code = alru_cache(maxsize=None)(dank_w3.eth.get_code)
