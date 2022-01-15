from typing import Any, Callable, KeysView, List, Tuple, Union

import brownie
from brownie.convert.datatypes import EthAddress
from eth_typing.evm import Address, BlockNumber
from ypricemagic.utils.multicall import (multicall_decimals,
                                         multicall_totalSupply)
from ypricemagic.utils.raw_calls import _decimals, _totalSupply

import y

SUPPORTED_INPUT_TYPES = str, Address, EthAddress, brownie.Contract, y.Contract


def decimals(
    contract_address_or_addresses: Union[str, Address, brownie.Contract, y.Contract, List[Union[str, Address, brownie.Contract, y.Contract]], Tuple[Union[str, Address, brownie.Contract, y.Contract]]],
    block: Union[BlockNumber, int, None] = None, 
    return_None_on_failure: bool = False
    ): 

    func = _choose_appropriate_fn(contract_address_or_addresses, _decimals, multicall_decimals)
    return func(contract_address_or_addresses, block=block, return_None_on_failure=return_None_on_failure)


def totalSupply(
    contract_address_or_addresses: Union[str, Address, brownie.Contract, y.Contract, List[Union[str, Address, brownie.Contract, y.Contract]], Tuple[Union[str, Address, brownie.Contract, y.Contract]]],
    block: Union[BlockNumber, int, None] = None, 
    return_None_on_failure: bool = False
    ):

    func = _choose_appropriate_fn(contract_address_or_addresses, _totalSupply, multicall_totalSupply)
    return func(contract_address_or_addresses, block=block, return_None_on_failure=return_None_on_failure)


def totalSupplyReadable(
    contract_address_or_addresses: Union[str, Address, brownie.Contract, y.Contract, List[Union[str, Address, brownie.Contract, y.Contract]], Tuple[Union[str, Address, brownie.Contract, y.Contract]]],
    block: Union[BlockNumber, int, None] = None, 
    return_None_on_failure: bool = False
    ):

    token_supplys = totalSupply(contract_address_or_addresses, block=block, return_None_on_failure=return_None_on_failure)
    token_decimals = decimals(contract_address_or_addresses, block=block, return_None_on_failure=return_None_on_failure)
    return [supply / 10 ** decimal for supply, decimal in zip(token_supplys, token_decimals)]


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
    
    if type(input) in [list, Tuple] or isinstance(input, KeysView): 
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
