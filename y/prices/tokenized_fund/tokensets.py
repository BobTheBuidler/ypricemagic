
import asyncio
import logging
from decimal import Decimal
from typing import List, Optional

import a_sync
from multicall import Call

from y import ENVIRONMENT_VARIABLES as ENVS
from y.classes.common import ERC20, WeiBalance
from y.contracts import Contract, has_methods
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.utils.cache import optional_async_diskcache

logger = logging.getLogger(__name__)


@a_sync.a_sync(default='sync', cache_type='memory', ram_cache_ttl=5*60)
@optional_async_diskcache
async def is_token_set(token: AnyAddressType) -> bool:
    return any(await asyncio.gather(
        has_methods(token, ("getComponents()(address[])", "naturalUnit()(uint)"), sync=False),
        has_methods(token, ("getComponents()(address[])", "getModules()(address[])", "getPositions()(address[])"), sync=False),
    ))

@a_sync.a_sync(default='sync')
async def get_price(token: AnyAddressType, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> UsdPrice:
    return await TokenSet(token, asynchronous=True).get_price(block=block, skip_cache=skip_cache)


class TokenSet(ERC20):
    def __init__(self, address: AnyAddressType, asynchronous: bool = False):
        super().__init__(address, asynchronous=asynchronous)
        self.get_total_component_real_units = Call(self.address, "getTotalComponentRealUnits(address)(int256)")

    @a_sync.a_sync(ram_cache_maxsize=100)
    async def components(self, block: Optional[Block] = None) -> List[ERC20]:
        contract = await Contract.coroutine(self.address)
        components = await contract.getComponents.coroutine(block_identifier = block)
        return [ERC20(component, asynchronous=self.asynchronous) for component in components]
    
    async def balances(self, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> List[WeiBalance]:
        contract, components = await asyncio.gather(
            Contract.coroutine(self.address),
            self.components(block=block, sync=False),
        )
        if hasattr(contract, 'getUnits'):
            balances = await contract.getUnits.coroutine(block_identifier = block)
            logger.debug("getUnits: %s", balances)
        elif hasattr(contract, 'getTotalComponentRealUnits'):
            _components = ((component.address, ) for component in components)
            balances = await a_sync.map(self.get_total_component_real_units.coroutine, _components, block_id=block).values(pop=True)
            logger.debug("getTotalComponentRealUnits: %s", balances)
        balances = [WeiBalance(balance, component, block=block, skip_cache=skip_cache) for component, balance in zip(components, balances)]
        return balances
    
    async def get_price(self, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> UsdPrice:
        total_supply = Decimal(await self.total_supply_readable(block=block, sync=False))
        if total_supply == 0:
            logger.debug("total supply is 0, forcing price to $0")
            return UsdPrice(0)
        contract = await Contract.coroutine(self.address)
        if hasattr(contract, "getUnits"):
            balances: List[WeiBalance] = await self.balances(block=block, skip_cache=skip_cache, sync=False)
            values = await WeiBalance.value_usd.map(balances).values(pop=True)
            logger.debug("balances: %s  values: %s", balances, values)
            tvl = sum(values)
            price = UsdPrice(tvl / total_supply)
            logger.debug("total supply: %s  tvl: %s  price: %s", total_supply, tvl, price)
            return price
        elif hasattr(contract, "getTotalComponentRealUnits"):
            balances_per_token: List[WeiBalance] = await self.balances(block=block, sync=False)
            price = UsdPrice(await WeiBalance.value_usd.sum(balances_per_token, sync=False))
            logger.debug("balances per token: %s  price: %s", balances_per_token, price)
            return price
        raise NotImplementedError
