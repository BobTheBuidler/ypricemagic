import logging
from functools import lru_cache
from typing import Any, List, Optional

from y.classes.common import ERC20, WeiBalance
from y.contracts import has_methods
from y.datatypes import UsdPrice
from y.decorators import log
from y.typing import AnyAddressType, Block
from y.utils.multicall import \
    multicall_same_func_same_contract_different_inputs

logger = logging.getLogger(__name__)

@log(logger)
@lru_cache
def is_token_set(token: AnyAddressType) -> bool:
    return any([
        has_methods(token, {"getComponents()(address[])", "naturalUnit()(uint)"}),
        has_methods(token, {"getComponents()(address[])", "getModules()(address[])", "getPositions()(address[])"})
    ])

@log(logger)
def get_price(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    return TokenSet(token).get_price(block=block)

class TokenSet(ERC20):
    def __init__(self, address: AnyAddressType, *args: Any, **kwargs: Any) -> None:
        super().__init__(address, *args, **kwargs)
    
    def components(self, block: Optional[Block] = None) -> List[ERC20]:
        components = self.contract.getComponents(block_identifier = block)
        return [ERC20(component) for component in components]
    
    def balances(self, block: Optional[Block] = None) -> List[WeiBalance]:
        if hasattr(self.contract, 'getUnits'):
            balances = self.contract.getUnits(block_identifier = block)
        elif hasattr(self.contract, 'getTotalComponentRealUnits'):
            balances = multicall_same_func_same_contract_different_inputs(
                self.address, 
                "getTotalComponentRealUnits(address)(uint)", 
                [component.address for component in self.components(block=block)
            ])
        return [WeiBalance(balance, component, block=block) for component, balance in zip(self.components(block=block), balances)]

    def get_price(self, block: Optional[Block] = None) -> UsdPrice:
        total_supply = self.total_supply_readable(block=block)
        if total_supply == 0:
            return UsdPrice(0)
        
        return UsdPrice(
            sum(balance.value_usd() for balance in self.balances(block=block))
        )
