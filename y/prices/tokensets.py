import logging
from functools import lru_cache
from typing import List

from y import totalSupplyReadable
from y.classes.common import ERC20, WeiBalance

from y.constants import usdc
from y.contracts import Contract, has_methods
from y.decorators import log
from y.prices import magic
from y.utils.multicall import \
    multicall_same_func_same_contract_different_inputs

logger = logging.getLogger(__name__)

@log(logger)
@lru_cache
def is_token_set(address):
    return any([
        has_methods(address, {"getComponents()(address[])", "naturalUnit()(uint)"}),
        has_methods(address, {"getComponents()(address[])", "getModules()(address[])", "getPositions()(address[])"})
    ])

@log(logger)
def get_price(token, block=None):
    #setValuer = Contract('0xDdF4F0775fF69c73619a4dBB42Ba61b0ac1F555f')
    #try:
    #    return setValuer.calculateSetTokenValuation(token, usdc, block_identifier=block)
    #except ValueError: # NOTE: This will run for v1 token sets
    return TokenSet(token).get_price(block=block)

class TokenSet(ERC20):
    def __init__(self, address: str, *args, **kwargs):
        super().__init__(address, *args, **kwargs)
    
    def components(self, block: int = None) -> List[ERC20]:
        components = self.contract.getComponents(block_identifier = block)
        return [ERC20(component) for component in components]
    
    def balances(self, block: int = None) -> List[WeiBalance]:
        if hasattr(self.contract, 'getUnits'):
            balances = self.contract.getUnits(block_identifier = block)
        elif hasattr(self.contract, 'getTotalComponentRealUnits'):
            balances = multicall_same_func_same_contract_different_inputs(
                self.address, 
                "getTotalComponentRealUnits(address)(uint)", 
                [component.address for component in self.components(block=block)
            ])
        return [WeiBalance(balance, component, block=block) for component, balance in zip(self.components(block=block), balances)]

    def get_price(self, block: int = None) -> float:
        total_supply = self.total_supply_readable(block=block)
        if total_supply == 0:
            return 0
        return sum(balance.value_usd() for balance in self.balances(block=block))