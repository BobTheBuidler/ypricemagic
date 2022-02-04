
import logging
from functools import cached_property, lru_cache
from typing import Union

from brownie import Contract as BrownieContract
from brownie import convert
from brownie.convert.datatypes import EthAddress
from brownie.exceptions import ContractNotFound
from eth_typing.evm import Address
from y.classes.singleton import ContractSingleton
from y.constants import EEE_ADDRESS
from y.contracts import Contract, build_name, has_method
from y.decorators import log
from y.erc20 import decimals, totalSupply
from y.exceptions import ContractNotVerified, MessedUpBrownieContract
from y.prices import magic
from y.utils.raw_calls import _name, _symbol

logger = logging.getLogger(__name__)


class ContractBase(metaclass=ContractSingleton):
    def __init__(self, address: str, *args, **kwargs):
        self.address = convert.to_address(address)
        super().__init__(*args, **kwargs)
    
    def __str__(self) -> str:
        return f'{self.address}'
    
    def __eq__(self, __o: object) -> bool:
        try: return convert.to_address(__o) == self.address
        except: return False
    
    def __hash__(self) -> int:
        return hash(self.address)
    
    @cached_property
    def contract(self) -> BrownieContract:
        return Contract(self.address)
    
    @cached_property
    @log(logger)
    def _is_cached(self) -> bool:
        try:
            self.contract
            return True
        except (ContractNotVerified):
            return False
        except (ContractNotFound, MessedUpBrownieContract):
            return None
    
    @cached_property
    @log(logger)
    def build_name(self):
        return build_name(self.address)
    
    @log(logger)
    @lru_cache
    def has_method(self, method: str, return_response: bool = False):
        return has_method(self.address, method, return_response=return_response)



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
        if self.address == EEE_ADDRESS:
            return "ETH"
        return _symbol(self.address, return_None_on_failure=True)
    
    @cached_property
    def name(self) -> str:
        if self.address == EEE_ADDRESS:
            return "Ethereum"
        return _name(self.address, return_None_on_failure=True)
    
    @cached_property
    def decimals(self) -> int:
        if self.address == EEE_ADDRESS:
            return 18
        return decimals(self.address)

    @log(logger)
    @lru_cache
    def _decimals(self, block: int = None) -> int:
        if self.address == EEE_ADDRESS:
            return 18
        '''used to fetch decimals at specific block'''
        return decimals(self.address, block=block)
    
    @cached_property
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
    def __init__(
        self, balance: int,
        token: Union[str, Address, BrownieContract, ContractBase, ERC20, EthAddress],
        block: int = None
        ) -> None:

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
    
    def value_usd(self) -> float:
        return self.readable * self.token.price(block=self.block)
