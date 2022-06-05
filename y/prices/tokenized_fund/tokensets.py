
import logging
from functools import lru_cache
from typing import Any, List, Optional

from async_lru import alru_cache
from multicall import Call
from multicall.utils import await_awaitable, gather
from y.classes.common import ERC20, WeiBalance
from y.contracts import has_methods_async
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.utils.logging import yLazyLogger

logger = logging.getLogger(__name__)

@yLazyLogger(logger)
@lru_cache(maxsize=None)
def is_token_set(token: AnyAddressType) -> bool:
    return await_awaitable(is_token_set_async(token))

@yLazyLogger(logger)
@alru_cache(maxsize=None)
async def is_token_set_async(token: AnyAddressType) -> bool:
    return any(await gather([
        has_methods_async(token, ("getComponents()(address[])", "naturalUnit()(uint)")),
        has_methods_async(token, ("getComponents()(address[])", "getModules()(address[])", "getPositions()(address[])")),
    ]))

@yLazyLogger(logger)
def get_price(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    return TokenSet(token).get_price(block=block)

@yLazyLogger(logger)
async def get_price_async(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    return await TokenSet(token).get_price_async(block=block)


class TokenSet(ERC20):
    def __init__(self, address: AnyAddressType, *args: Any, **kwargs: Any) -> None:
        super().__init__(address, *args, **kwargs)
    
    @lru_cache(maxsize=100)
    def components(self, block: Optional[Block] = None) -> List[ERC20]:
        components = self.contract.getComponents(block_identifier = block)
        return [ERC20(component) for component in components]
    
    def balances(self, block: Optional[Block] = None) -> List[WeiBalance]:
        return await_awaitable(self.balances_async(block=block))
    
    async def balances_async(self, block: Optional[Block] = None) -> List[WeiBalance]:
        if hasattr(self.contract, 'getUnits'):
            balances = await self.contract.getUnits.coroutine(block_identifier = block)
        elif hasattr(self.contract, 'getTotalComponentRealUnits'):
            balances = await gather([
                Call(self.address, ["getTotalComponentRealUnits(address)(uint)",component.address], [[component.address, None]], block_id=block).coroutine()
                for component in self.components(block)
            ])
            '''
            balances = await multicall_same_func_same_contract_different_inputs_async(
                self.address, 
                "getTotalComponentRealUnits(address)(uint)", 
                [component.address for component in self.components(block=block)
            ])
            '''
        return [WeiBalance(balance, component, block=block) for component, balance in zip(self.components(block=block), balances)]

    def get_price(self, block: Optional[Block] = None) -> UsdPrice:
        return await_awaitable(self.get_price_async(block=block))
    
    async def get_price_async(self, block: Optional[Block] = None) -> UsdPrice:
        total_supply = await self.total_supply_readable_async(block=block)
        if total_supply == 0:
            return UsdPrice(0)
        return UsdPrice(sum(await gather([balance.value_usd_async for balance in self.balances(block=block)])))
