
import logging
from functools import cached_property, lru_cache
from typing import Union

from brownie import Contract, convert
from y.classes.singleton import ContractSingleton
from y.decorators import log
from y.erc20 import decimals, totalSupply
from ypricemagic import magic
from ypricemagic.utils.raw_calls import _symbol, _name

logger = logging.getLogger(__name__)


class ContractBase(metaclass=ContractSingleton):
    def __init__(self, address: str, *args, **kwargs):
        self.address = convert.to_address(address)
        super().__init__(*args, **kwargs)
    
    def __str__(self) -> str:
        return self.address
    
    def __eq__(self, __o: object) -> bool:
        try: return convert.to_address(__o) == self.address
        except: return False
    
    def __hash__(self) -> int:
        return hash(self.address)


class ERC20(ContractBase):
    def __init__(self, address: str, *args, **kwargs):
        super().__init__(address, *args, **kwargs)
    
    def __repr__(self) -> str:
        if self.symbol is None:
            return f"<ERC20 '{self.address}'>"
        else:
            return f"<ERC20 {self.symbol} '{self.address}'>"
    
    @cached_property
    def symbol(self) -> str:
        return _symbol(self.address, return_None_on_failure=True)
    
    @cached_property
    def name(self) -> str:
        return _name(self.address, return_None_on_failure=True)
    
    @cached_property
    def decimals(self) -> int:
        return decimals(self.address)

    @log(logger)
    @lru_cache
    def _decimals(self, block: int = None) -> int:
        '''used to fetch decimals at specific block'''
        return decimals(self.address, block=block)
    
    @log(logger)
    def scale(self) -> int:
        return 10 ** self.decimals
    
    @log(logger)
    def _scale(self, block: int = None) -> int:
        return 10 ** self._decimals(block=block)

    @log(logger)
    @lru_cache
    def total_supply(self, block: int = None) -> int:
        return totalSupply(self.address, block=block)
    
    @log(logger)
    def total_supply_readable(self, block: int = None) -> float:
        return self.total_supply(block=block) / self._scale(block=block)

    @log(logger)
    def price(self, block: int = None, return_None_on_failure: bool = False) -> float:
        return magic.get_price(
            self.address, 
            block=block, 
            fail_to_None=return_None_on_failure
        )

class WeiBalance:
    def __init__(self, balance: int, token: Union[str, Contract, ERC20], block: int = None) -> None:
        self.balance = balance
        self.token = ERC20(str(token))
        self.block = block
        super().__init__()

    def __str__(self) -> str:
        return str(self.balance)

    def __eq__(self, __o: object) -> bool:
        return __o == self.balance
    
    @cached_property
    def readable(self) -> float:
        return self.balance / self.token._scale(block=self.block)
