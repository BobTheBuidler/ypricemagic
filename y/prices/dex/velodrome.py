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
