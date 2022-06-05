
import logging
from functools import cached_property, lru_cache
from typing import Any, Optional, Union

import brownie
from async_property import async_cached_property, async_property
from brownie.exceptions import ContractNotFound
from multicall.utils import await_awaitable, gather
from y import convert
from y.classes.singleton import ContractSingleton
from y.constants import EEE_ADDRESS
from y.contracts import Contract, build_name, has_method, has_method_async
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.erc20 import decimals_async, totalSupply_async
from y.exceptions import ContractNotVerified, MessedUpBrownieContract
from y.prices import magic
from y.utils.logging import yLazyLogger
from y.utils.raw_calls import _name, _symbol, _symbol_async

logger = logging.getLogger(__name__)


class ContractBase(metaclass=ContractSingleton):
    def __init__(self, address: AnyAddressType, *args: Any, **kwargs: Any) -> None:
        self.address = convert.to_address(address)
        super().__init__(*args, **kwargs)
    
    def __str__(self) -> str:
        return f'{self.address}'
    
    def __eq__(self, __o: object) -> bool:
        try:
            return convert.to_address(__o) == self.address
        except:
            return False
    
    def __hash__(self) -> int:
        return hash(self.address)
    
    @cached_property
    def contract(self) -> brownie.Contract:
        return Contract(self.address)
    
    @cached_property
    @yLazyLogger(logger)
    def _is_cached(self) -> bool:
        try:
            self.contract
            return True
        except (ContractNotVerified):
            return False
        except (ContractNotFound, MessedUpBrownieContract):
            return None
    
    @cached_property
    @yLazyLogger(logger)
    def build_name(self) -> str:
        return build_name(self.address)
    
    @yLazyLogger(logger)
    @lru_cache
    def has_method(self, method: str, return_response: bool = False) -> Union[bool,Any]:
        return has_method(self.address, method, return_response=return_response)
    
    async def has_method_async(self, method: str, return_response: bool = False) -> Union[bool,Any]:
        return await has_method_async(self.address, method, return_response=return_response)


class ERC20(ContractBase):
    def __init__(self, address: AnyAddressType, *args: Any, **kwargs: Any) -> None:
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

    @async_cached_property
    async def symbol_async(self) -> str:
        if self.address == EEE_ADDRESS:
            return "ETH"
        return await _symbol_async(self.address, return_None_on_failure=True)
    
    @async_cached_property
    async def name(self) -> str:
        if self.address == EEE_ADDRESS:
            return "Ethereum"
        return await _name(self.address, return_None_on_failure=True)
    
    @yLazyLogger(logger)
    @async_cached_property
    async def decimals(self) -> int:
        if self.address == EEE_ADDRESS:
            return 18
        return await decimals_async(self.address)

    @yLazyLogger(logger)
    async def _decimals(self, block: Optional[Block] = None) -> int:
        '''used to fetch decimals at specific block'''
        if self.address == EEE_ADDRESS:
            return 18
        return await decimals_async(self.address, block=block)
    
    @yLazyLogger(logger)
    @async_cached_property
    async def scale(self) -> int:
        return 10 ** await self.decimals
    
    @yLazyLogger(logger)
    async def _scale(self, block: Optional[Block] = None) -> int:
        return 10 ** await self._decimals(block=block)

    def total_supply(self, block: Optional[Block] = None) -> int:
        return await_awaitable(self.total_supply_async(block=block))

    @yLazyLogger(logger)
    async def total_supply_async(self, block: Optional[Block] = None) -> int:
        return await totalSupply_async(self.address, block=block)
    
    def total_supply_readable(self, block: Optional[Block] = None) -> float:
        return await_awaitable(self.total_supply_readable_async(block=block))

    @yLazyLogger(logger)
    async def total_supply_readable_async(self, block: Optional[Block] = None) -> float:
        total_supply, scale = await gather([self.total_supply_async(block=block), self.scale])
        return total_supply / scale

    @yLazyLogger(logger)
    def price(self, block: Optional[Block] = None, return_None_on_failure: bool = False) -> Optional[UsdPrice]:
        return await_awaitable(
            self.price_async(block=block, return_None_on_failure=return_None_on_failure)
        )

    @yLazyLogger(logger)
    async def price_async(self, block: Optional[Block] = None, return_None_on_failure: bool = False) -> Optional[UsdPrice]:
        return await magic.get_price_async(
            self.address, 
            block=block, 
            fail_to_None=return_None_on_failure
        )

class WeiBalance:
    def __init__(
        self, balance: int,
        token: AnyAddressType,
        block: Optional[Block] = None
        ) -> None:

        self.balance = balance
        self.token = ERC20(str(token))
        self.block = block
        super().__init__()

    def __str__(self) -> str:
        return str(self.balance)

    def __eq__(self, __o: object) -> bool:
        return __o == self.balance
    
    @property
    def readable(self) -> float:
        return await_awaitable(self.readable_async)
    
    @async_property
    async def readable_async(self) -> float:
        if self.balance == 0:
            return 0
        return self.balance / await self.token.scale

    @property
    def value_usd(self) -> float:
        return await_awaitable(self.value_usd_async)
    
    @async_property
    async def value_usd_async(self) -> float:
        if self.balance == 0:
            return 0
        balance, price = await gather([
            self.readable_async,
            self.token.price_async(block=self.block),
        ])
        return balance * price
