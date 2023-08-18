
import asyncio
from typing import List, Optional, Tuple

import a_sync

from y import ENVIRONMENT_VARIABLES as ENVS
from y.datatypes import Address, Block
from y.decorators import continue_on_revert
from y.exceptions import call_reverted
from y.prices.dex.uniswap.v2 import Path, UniswapV2Pool, UniswapRouterV2


class SolidlyRouterBase(UniswapRouterV2):
    """
    Solidly is a modified fork of Uni V2.
    The `uniswap_multiplexer` is the entrypoint for pricing using this object.
    """
        
    @continue_on_revert
    async def get_quote(self, amount_in: int, path: Path, block: Optional[Block] = None) -> Tuple[int,int]:
        routes = await self.get_routes_from_path(path, block)
        try:
            return await self.contract.getAmountsOut.coroutine(amount_in, routes, block_identifier=block)
        # TODO figure out how to best handle uni forks with slight modifications.
        # Sometimes the below "else" code will not work with modified methods. Brownie works for now.
        except Exception as e:
            strings = [
                "INSUFFICIENT_INPUT_AMOUNT",
                "INSUFFICIENT_LIQUIDITY",
                "INSUFFICIENT_OUT_LIQUIDITY",
                "Sequence has incorrect length",
            ]
            if not call_reverted(e) and not any(s in str(e) for s in strings):
                raise e
    

class SolidlyRouter(SolidlyRouterBase):

    @a_sync.a_sync(ram_cache_ttl=ENVS.CACHE_TTL)
    async def pair_for(self, input_token: Address, output_token: Address, stable: bool) -> Address:
        return await self.contract.pairFor.coroutine(input_token, output_token, stable)
    
    @a_sync.a_sync(ram_cache_ttl=ENVS.CACHE_TTL)
    async def get_pool(self, input_token: Address, output_token: Address, stable: bool, block: Block) -> Optional[UniswapV2Pool]:
        pool_address = await self.pair_for(input_token, output_token, stable, sync=False)
        if await self.contract.isPair.coroutine(pool_address, block_identifier=block):
            return UniswapV2Pool(pool_address)

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
                routes.append([input_token, output_token, is_stable])
            elif stable_pool:
                routes.append([input_token, output_token, True])
            elif unstable_pool:
                routes.append([input_token, output_token, False])
            else:
                raise ValueError("Not sure why this function is even running if no pool is found")
            
        return routes