import logging
from typing import Any, Callable, KeysView, List, Optional, Tuple, Union

import a_sync
import brownie
from a_sync import cgather
from brownie.convert.datatypes import EthAddress

from y.contracts import Contract
from y.datatypes import Address, AddressOrContract, Block
from y.utils.multicall import multicall_decimals, multicall_totalSupply
from y.utils.raw_calls import _decimals, _totalSupply

logger = logging.getLogger(__name__)

SUPPORTED_INPUT_TYPES = str, Address, EthAddress, brownie.Contract, Contract

# These helpers can be used to fetch values for one or more tokens at once.
# NOTE You shoulnd't use these, they will likely be deleted soon for a cleaner alternative.


@a_sync.a_sync(default="sync")
async def decimals(
    contract_address_or_addresses: Union[
        AddressOrContract, List[AddressOrContract], Tuple[AddressOrContract]
    ],
    block: Optional[Block] = None,
    return_None_on_failure: bool = False,
):
    """
    Fetch the decimals for one or more ERC20 tokens.

    This function determines the appropriate method to use for fetching decimals
    based on the input type (single or multiple addresses).

    NOTE: You shouldn't use this function, it will likely be deleted soon for a cleaner alternative.

    Args:
        contract_address_or_addresses: A single address or a list/tuple of addresses of ERC20 tokens.
        block: The block number at which to fetch the decimals. Defaults to the latest block.
        return_None_on_failure: If True, return None on failure instead of raising an exception.

    Examples:
        Fetch decimals for a single token:

        >>> decimals("0x6B175474E89094C44Da98b954EedeAC495271d0F")
        18

        Fetch decimals for multiple tokens:

        >>> decimals(["0x6B175474E89094C44Da98b954EedeAC495271d0F", "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"])
        [18, 6]

    See Also:
        - :func:`y.utils.raw_calls._decimals`
        - :func:`y.utils.multicall.multicall_decimals`
    """
    func = _choose_appropriate_fn(
        contract_address_or_addresses, _decimals, multicall_decimals
    )
    return await func(
        contract_address_or_addresses,
        block=block,
        return_None_on_failure=return_None_on_failure,
        sync=False,
    )


@a_sync.a_sync(default="sync")
async def totalSupply(
    contract_address_or_addresses: Union[
        AddressOrContract, List[AddressOrContract], Tuple[AddressOrContract]
    ],
    block: Optional[Block] = None,
    return_None_on_failure: bool = False,
):
    """
    Fetch the total supply for one or more ERC20 tokens.

    This function determines the appropriate method to use for fetching total supply
    based on the input type (single or multiple addresses).

    NOTE: You shouldn't use this function, it will likely be deleted soon for a cleaner alternative.

    Args:
        contract_address_or_addresses: A single address or a list/tuple of addresses of ERC20 tokens.
        block: The block number at which to fetch the total supply. Defaults to the latest block.
        return_None_on_failure: If True, return None on failure instead of raising an exception.

    Examples:
        Fetch total supply for a single token:

        >>> totalSupply("0x6B175474E89094C44Da98b954EedeAC495271d0F")
        1000000000000000000000000

        Fetch total supply for multiple tokens:

        >>> totalSupply(["0x6B175474E89094C44Da98b954EedeAC495271d0F", "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"])
        [1000000000000000000000000, 500000000000000000000000]

    See Also:
        - :func:`y.utils.raw_calls._totalSupply`
        - :func:`y.utils.multicall.multicall_totalSupply`
    """
    func = _choose_appropriate_fn(
        contract_address_or_addresses, _totalSupply, multicall_totalSupply
    )
    return await func(
        contract_address_or_addresses,
        block=block,
        return_None_on_failure=return_None_on_failure,
        sync=False,
    )


@a_sync.a_sync(default="sync")
async def totalSupplyReadable(
    contract_address_or_addresses: Union[
        AddressOrContract, List[AddressOrContract], Tuple[AddressOrContract]
    ],
    block: Optional[Block] = None,
    return_None_on_failure: bool = False,
):
    """
    Fetch the total supply for one or more ERC20 tokens and convert it to a human-readable format.

    This function fetches the total supply and decimals for the given tokens and returns
    the total supply divided by 10^decimals.

    NOTE: You shouldn't use this function, it will likely be deleted soon for a cleaner alternative.

    Args:
        contract_address_or_addresses: A single address or a list/tuple of addresses of ERC20 tokens.
        block: The block number at which to fetch the total supply. Defaults to the latest block.
        return_None_on_failure: If True, return None on failure instead of raising an exception.

    Examples:
        Fetch human-readable total supply for a single token:

        >>> totalSupplyReadable("0x6B175474E89094C44Da98b954EedeAC495271d0F")
        1000000.0

        Fetch human-readable total supply for multiple tokens:

        >>> totalSupplyReadable(["0x6B175474E89094C44Da98b954EedeAC495271d0F", "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"])
        [1000000.0, 500000.0]

    See Also:
        - :func:`totalSupply`
        - :func:`decimals`
    """
    token_supplys, token_decimals = await cgather(
        totalSupply(
            contract_address_or_addresses,
            block=block,
            return_None_on_failure=return_None_on_failure,
            sync=False,
        ),
        decimals(
            contract_address_or_addresses,
            block=block,
            return_None_on_failure=return_None_on_failure,
            sync=False,
        ),
    )

    if type(token_supplys) == brownie.Wei:  # if only fetching totalSupply for one token
        supply = token_supplys
        decimal = token_decimals
        return supply / 10**decimal
    return [
        supply / 10**decimal for supply, decimal in zip(token_supplys, token_decimals)
    ]


def _choose_appropriate_fn(input: Any, singlecall_fn: Callable, multicall_fn: Callable):
    """
    Choose the appropriate function based on the input type.

    This helper function determines whether to use a single call or multicall function
    based on whether the input is a single address or multiple addresses.

    Args:
        input: The input to check.
        singlecall_fn: The function to use for a single address.
        multicall_fn: The function to use for multiple addresses.

    Returns:
        The appropriate function to use.

    Examples:
        Choose function for a single address:

        >>> _choose_appropriate_fn("0x6B175474E89094C44Da98b954EedeAC495271d0F", single_fn, multi_fn)
        <function single_fn>

        Choose function for multiple addresses:

        >>> _choose_appropriate_fn(["0x6B175474E89094C44Da98b954EedeAC495271d0F", "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"], single_fn, multi_fn)
        <function multi_fn>
    """
    input_type = _input_type(input)
    if input_type == "single":
        return singlecall_fn
    elif input_type == "multi":
        return multicall_fn


def _input_type(input: Any) -> str:
    """
    Determine the input type (single or multiple).

    This helper function checks if the input is a single address or multiple addresses.

    Args:
        input: The input to check.

    Returns:
        A string indicating the input type ("single" or "multi").

    Examples:
        Determine input type for a single address:

        >>> _input_type("0x6B175474E89094C44Da98b954EedeAC495271d0F")
        'single'

        Determine input type for multiple addresses:

        >>> _input_type(["0x6B175474E89094C44Da98b954EedeAC495271d0F", "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"])
        'multi'
    """
    if type(input) in [list, tuple] or isinstance(input, KeysView):
        for value in input:
            _check_if_supported(value)
        return "multi"
    else:
        _check_if_supported(input)
        return "single"


def _check_if_supported(input: Any) -> bool:
    """
    Check if the input type is supported.

    This helper function raises a TypeError if the input type is not supported.

    Args:
        input: The input to check.

    Returns:
        True if the input type is supported.

    Raises:
        TypeError: If the input type is not supported.

    Examples:
        Check if a valid address is supported:

        >>> _check_if_supported("0x6B175474E89094C44Da98b954EedeAC495271d0F")
        True

        Check if an invalid input type raises an error:

        >>> _check_if_supported(123)
        Traceback (most recent call last):
        ...
        TypeError: Unsupported input type: <class 'int'>
    """
    if type(input) not in SUPPORTED_INPUT_TYPES:
        raise TypeError(f"Unsupported input type: {type(input)}")
