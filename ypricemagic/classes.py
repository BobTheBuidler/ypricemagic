from decimal import Decimal
from functools import cached_property, lru_cache

from y.contracts import Contract, build_name

from ypricemagic.utils.raw_calls import _name, _symbol, _totalSupplyReadable


# WIP
class ERC20:
    def __init__(self, token_address) -> None:
        self.address = token_address
    
    @cached_property
    def contract(self):
        return Contract(self.address)

    @cached_property
    def build_name(self):
        return build_name(self.address)
    
    @cached_property
    def symbol(self):
        return _symbol(self.address)
    
    @cached_property
    def name(self):
        return _name(self.address)

    def total_supply(self, block=None) -> Decimal:
        return _totalSupplyReadable(self.address, block)

