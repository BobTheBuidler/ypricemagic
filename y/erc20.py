import logging
from typing import Any, Callable, KeysView, List, Optional, Tuple, Union

import brownie
from brownie.convert.datatypes import EthAddress
from multicall.utils import await_awaitable, gather

from y.contracts import Contract
from y.datatypes import Address, AddressOrContract, Block
from y.utils.multicall import (multicall_decimals_async, multicall_totalSupply,
                               multicall_totalSupply_async)
from y.utils.raw_calls import _decimals, _totalSupply

logger = logging.getLogger(__name__)

SUPPORTED_INPUT_TYPES = str, Address, EthAddress, brownie.Contract, Contract

# These helpers can be used to fetch values for one or more tokens at once.

def decimals(
    contract_address_or_addresses: Union[AddressOrContract,List[AddressOrContract],Tuple[AddressOrContract]],
    block: Optional[Block] = None, 
    return_None_on_failure: bool = False
    ): 
    return await_awaitable(
        decimals_async(contract_address_or_addresses, block=block, return_None_on_failure=return_None_on_failure)
    )


async def decimals_async(
    contract_address_or_addresses: Union[AddressOrContract,List[AddressOrContract],Tuple[AddressOrContract]],
    block: Optional[Block] = None, 
    return_None_on_failure: bool = False
    ): 

    func = _choose_appropriate_fn(contract_address_or_addresses, _decimals, multicall_decimals_async)
    return await func(contract_address_or_addresses, block=block, return_None_on_failure=return_None_on_failure)


def totalSupply(
    contract_address_or_addresses: Union[AddressOrContract,List[AddressOrContract],Tuple[AddressOrContract]],
    block: Optional[Block] = None, 
    return_None_on_failure: bool = False
    ):
    return await_awaitable(
        totalSupply_async(contract_address_or_addresses, block=block, return_None_on_failure=return_None_on_failure)
    )


async def totalSupply_async(
    contract_address_or_addresses: Union[AddressOrContract,List[AddressOrContract],Tuple[AddressOrContract]],
    block: Optional[Block] = None, 
    return_None_on_failure: bool = False
    ):

    func = _choose_appropriate_fn(contract_address_or_addresses, _totalSupply, multicall_totalSupply_async)
    return await func(contract_address_or_addresses, block=block, return_None_on_failure=return_None_on_failure)


def totalSupplyReadable(
    contract_address_or_addresses: Union[AddressOrContract,List[AddressOrContract],Tuple[AddressOrContract]],
    block: Optional[Block] = None, 
    return_None_on_failure: bool = False
    ):
    return await_awaitable(
        totalSupplyReadable_async(contract_address_or_addresses, block=block, return_None_on_failure=return_None_on_failure)
    )


async def totalSupplyReadable_async(
    contract_address_or_addresses: Union[AddressOrContract,List[AddressOrContract],Tuple[AddressOrContract]],
    block: Optional[Block] = None, 
    return_None_on_failure: bool = False
    ):

    token_supplys, token_decimals = await gather([
        totalSupply_async(contract_address_or_addresses, block=block, return_None_on_failure=return_None_on_failure),
        decimals_async(contract_address_or_addresses, block=block, return_None_on_failure=return_None_on_failure),
    ])

    if type(token_supplys) == brownie.Wei: # if only fetching totalSupply for one token
        supply = token_supplys
        decimal = token_decimals
        return supply / 10 ** decimal
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
