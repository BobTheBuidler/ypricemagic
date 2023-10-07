
import asyncio
import logging
from decimal import Decimal
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
    def __init__(self, address: AnyAddressType, asynchronous: bool = False):
        super().__init__(address, asynchronous=asynchronous)
        self.get_total_component_real_units = Call(self.address, "getTotalComponentRealUnits(address)(int256)")

    @a_sync.a_sync(ram_cache_maxsize=100)
    async def components(self, block: Optional[Block] = None) -> List[ERC20]:
        components = await self.contract.getComponents.coroutine(block_identifier = block)
        return [ERC20(component, asynchronous=self.asynchronous) for component in components]
    
    async def balances(self, block: Optional[Block] = None) -> List[WeiBalance]:
        if hasattr(self.contract, 'getUnits'):
            balances = await self.contract.getUnits.coroutine(block_identifier = block)
            logger.debug("getUnits: %s", balances)
        elif hasattr(self.contract, 'getTotalComponentRealUnits'):
            balances = await asyncio.gather(*[
                self.get_total_component_real_units.coroutine((component.address, ), block_id=block)
                for component in await self.components(block, sync=False)
            ])
            logger.debug("getTotalComponentRealUnits: %s", balances)
        balances = [WeiBalance(balance, component, block=block) for component, balance in zip(await self.components(block=block, sync=False), balances)]
        return balances
    
    async def get_price(self, block: Optional[Block] = None) -> UsdPrice:
        total_supply = Decimal(await self.total_supply_readable(block=block, sync=False))
        if total_supply == 0:
            logger.debug("total supply is 0, forcing price to $0")
            return UsdPrice(0)
        if hasattr(self.contract, "getUnits"):
            balances = await self.balances(block=block, sync=False)
            values = await asyncio.gather(*[balance.__value_usd__(sync=False) for balance in balances])
            logger.debug("balances: %s  values: %s", balances, values)
            tvl = sum(values)
            price = UsdPrice(tvl / total_supply)
            logger.debug("total supply: %s  tvl: %s  price: %s", total_supply, tvl, price)
            return price
        elif hasattr(self.contract, "getTotalComponentRealUnits"):
            balances_per_token = await self.balances(block=block, sync=False)
            values_per_token = await asyncio.gather(*[balance.__value_usd__(sync=False) for balance in balances_per_token])
            price = UsdPrice(sum(values_per_token))
            logger.debug("balances per token: %s  values per token: %s  price: %s", balances_per_token, values_per_token, price)
            return price
        raise NotImplementedError
