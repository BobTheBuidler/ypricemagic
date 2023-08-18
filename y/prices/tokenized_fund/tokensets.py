
import asyncio
import logging
from typing import List, Optional

import a_sync
from multicall import Call

from y.classes.common import ERC20, WeiBalance
from y.contracts import has_methods
from y.datatypes import AnyAddressType, Block, UsdPrice

logger = logging.getLogger(__name__)


@a_sync.a_sync(default='sync', cache_type='memory')
async def is_token_set(token: AnyAddressType) -> bool:
    return any(await asyncio.gather(
        has_methods(token, ("getComponents()(address[])", "naturalUnit()(uint)"), sync=False),
        has_methods(token, ("getComponents()(address[])", "getModules()(address[])", "getPositions()(address[])"), sync=False),
    ))

@a_sync.a_sync(default='sync')
async def get_price(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    return await TokenSet(token, asynchronous=True).get_price(block=block)


class TokenSet(ERC20):
    @a_sync.a_sync(ram_cache_maxsize=100)
    async def components(self, block: Optional[Block] = None) -> List[ERC20]:
        components = await self.contract.getComponents.coroutine(block_identifier = block)
        return [ERC20(component, asynchronous=self.asynchronous) for component in components]
    
    async def balances(self, block: Optional[Block] = None) -> List[WeiBalance]:
        if hasattr(self.contract, 'getUnits'):
            balances = await self.contract.getUnits.coroutine(block_identifier = block)
        elif hasattr(self.contract, 'getTotalComponentRealUnits'):
            balances = await asyncio.gather(*[
                Call(self.address, ["getTotalComponentRealUnits(address)(uint)", component.address], block_id=block).coroutine()
                for component in await self.components(block, sync=False)
            ])
        return [WeiBalance(balance, component, block=block) for component, balance in zip(await self.components(block=block, sync=False), balances)]
    
    async def get_price(self, block: Optional[Block] = None) -> UsdPrice:
        total_supply = await self.total_supply_readable(block=block, sync=False)
        if total_supply == 0:
            return UsdPrice(0)
        tvl = sum(await asyncio.gather(*[balance.__value_usd__(sync=False) for balance in await self.balances(block=block, sync=False)]))
        return UsdPrice(tvl / total_supply)
