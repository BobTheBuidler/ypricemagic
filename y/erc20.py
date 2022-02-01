import logging
from functools import cached_property, lru_cache
from typing import Any, Callable, KeysView, List, Tuple, Union

import brownie
from brownie import convert
from y.decorators import log
from brownie.convert.datatypes import EthAddress
from eth_typing.evm import Address, BlockNumber
from ypricemagic import magic
from ypricemagic.utils.multicall import (multicall_decimals,
                                         multicall_totalSupply)
from ypricemagic.utils.raw_calls import _decimals, _totalSupply

from y.contracts import Contract

logger = logging.getLogger(__name__)

SUPPORTED_INPUT_TYPES = str, Address, EthAddress, brownie.Contract, Contract


def decimals(
    contract_address_or_addresses: Union[str, Address, brownie.Contract, Contract, List[Union[str, Address, brownie.Contract, Contract]], Tuple[Union[str, Address, brownie.Contract, Contract]]],
    block: Union[BlockNumber, int, None] = None, 
    return_None_on_failure: bool = False
    ): 

    func = _choose_appropriate_fn(contract_address_or_addresses, _decimals, multicall_decimals)
    return func(contract_address_or_addresses, block=block, return_None_on_failure=return_None_on_failure)


def totalSupply(
    contract_address_or_addresses: Union[str, Address, brownie.Contract, Contract, List[Union[str, Address, brownie.Contract, Contract]], Tuple[Union[str, Address, brownie.Contract, Contract]]],
    block: Union[BlockNumber, int, None] = None, 
    return_None_on_failure: bool = False
    ):

    func = _choose_appropriate_fn(contract_address_or_addresses, _totalSupply, multicall_totalSupply)
    return func(contract_address_or_addresses, block=block, return_None_on_failure=return_None_on_failure)


def totalSupplyReadable(
    contract_address_or_addresses: Union[str, Address, brownie.Contract, Contract, List[Union[str, Address, brownie.Contract, Contract]], Tuple[Union[str, Address, brownie.Contract, Contract]]],
    block: Union[BlockNumber, int, None] = None, 
    return_None_on_failure: bool = False
    ):

    token_supplys = totalSupply(contract_address_or_addresses, block=block, return_None_on_failure=return_None_on_failure)
    token_decimals = decimals(contract_address_or_addresses, block=block, return_None_on_failure=return_None_on_failure)

    if type(token_supplys) == brownie.Wei: # if only fetching totalSupply for one token
        supply = token_supplys
        decimal = token_decimals
        return supply / 10 ** decimal
    return [supply / 10 ** decimal for supply, decimal in zip(token_supplys, token_decimals)]


class ERC20:
    def __init__(self, address: str) -> None:
        self.address = convert.to_address(address)
        pass

    @log(logger)
    @lru_cache
    def decimals(self, block: int = None) -> int:
        return decimals(self.address, block=block)
    
    @log(logger)
    def scale(self, block: int = None) -> int:
        return 10 ** self.decimals(block=block)

    @log(logger)
    @lru_cache
    def total_supply(self, block: int = None) -> int:
        return totalSupply(self.address, block=block)
    
    @log(logger)
    def total_supply_readable(self, block: int = None) -> float:
        return self.total_supply(block=block) / self.scale(block=block)

    @log(logger)
    def price(self, block: int = None, return_None_on_failure: bool = False) -> float:
        return magic.get_price(
            self.address, 
            block=block, 
            fail_to_None=return_None_on_failure
        )


def _choose_appropriate_fn(
    input: Any,
    singlecall_fn: Callable,
    multicall_fn: Callable
    ):

    input_type = _input_type(input)
    if input_type == 'single': return singlecall_fn
    elif input_type == 'multi': return multicall_fn


def _input_type(
    input: Any
    ) -> str:
    
    if type(input) in [list, tuple] or isinstance(input, KeysView): 
        for value in input: _check_if_supported(value)
        return 'multi'
    
    else:
        _check_if_supported(input)
        return 'single'


def _check_if_supported(
    input: Any
    ) -> bool:
    
    if type(input) not in SUPPORTED_INPUT_TYPES:
        raise TypeError(f'Unsupported input type: {type(input)}')