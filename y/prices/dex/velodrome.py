from typing import List, Optional, Tuple

from brownie import convert

import a_sync
from y.networks import Network
from y.datatypes import Address, AnyAddressType, Block
from y.exceptions import CantFindSwapPath, call_reverted
from y.decorators import continue_on_revert
from y.prices.dex.uniswap.v2 import UniswapRouterV2, Path


class VelodromeRouterV1(UniswapRouterV2):
    """
    Velo V1 is a modified fork of Uni V2.
    The `uniswap_multiplexer` is the entrypoint for pricing using this object.
    """

    async def get_routes_from_path(self, path: Path, block: Block) -> List[Tuple[Address, Address, bool]]:
        routes = []
        for i in range(len(path) - 1):
            input_token, output_token = path[i], path[i+1]
            # Try for a stable pool first and use that if available
            stable_pool_address = await self.contract.pairFor.coroutine(input_token, output_token, True, block_identifier=block)
            if await self.contract.isPair.coroutine(stable_pool_address, block_identifier=block):
                is_stable = True
            else:
                unstable_pool_address = await self.contract.pairFor.coroutine(input_token, output_token, False, block_identifier=block)
                if not await self.contract.isPair.coroutine(unstable_pool_address, block_identifier=block):
                    raise ValueError(
                        f"router shows no pair for {input_token} and {output_token}",
                        "If neither a stable nor unstable pool are available, this function shouldn't even be running."
                    )
                is_stable = False
            routes.append([input_token, output_token, is_stable])
        return routes

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
    '''
    @a_sync.a_sync(ram_cache_maxsize=500)
    async def get_path_to_stables(self, token: AnyAddressType, block: Optional[Block] = None, _loop_count: int = 0, _ignore_pools: Tuple[Address,...] = ()) -> List[Tuple[Address, Address, bool]]:
        if _loop_count > 10:
            raise CantFindSwapPath
        token_address = convert.to_address(token)
        path = [token_address]
        deepest_pool = await self.deepest_pool(token_address, block, _ignore_pools, sync=False)
        if deepest_pool:
            paired_with = (await self.__pool_mapping__(sync=False))[token_address][deepest_pool]
            deepest_stable_pool = await self.deepest_stable_pool(token_address, block, sync=False)
            if deepest_stable_pool and deepest_pool == deepest_stable_pool:
                last_step = (await self.__pool_mapping__(sync=False))[token_address][deepest_stable_pool]
                path.append(last_step)
                return path

            if path == [token_address]:
                try:
                    path.extend(
                        await self.get_path_to_stables(
                            paired_with,
                            block=block, 
                            _loop_count=_loop_count+1, 
                            _ignore_pools=tuple(list(_ignore_pools) + [deepest_pool]),
                            sync=False,
                        )
                    )
                except CantFindSwapPath:
                    pass

        if path == [token_address]:
            raise CantFindSwapPath(f'Unable to find swap path for {token_address} on {Network.printable()}')

        routes = []
        for i in range(len(path) - 1):
            input_token, output_token = path[i], path[i+1]
            # Try for a stable pool first and use that if available
            stable_pool_address = await self.contract.pairFor.coroutine(input_token, output_token, True, block_identifier=block)
            if await self.contract.isPair.coroutine(stable_pool_address, block_identifier=block):
                is_stable = True
            else:
                unstable_pool_address = await self.contract.pairFor.coroutine(input_token, output_token, False, block_identifier=block)
                if not await self.contract.isPair.coroutine(unstable_pool_address, block_identifier=block):
                    # If neither a stable nor unstable pool are available, this function shouldn't even be running.
                    raise ValueError(f"router shows no pair for {input_token} and {output_token}")
                is_stable = False
            routes.append([input_token, output_token, is_stable])
        return routes
    '''