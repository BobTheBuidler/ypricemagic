import contextlib
import logging
from typing import Any, Callable, Optional, Union

import a_sync
import brownie
import dank_mids
from a_sync import cgather
from brownie import ZERO_ADDRESS, convert
from brownie.convert.datatypes import EthAddress
from eth_utils import encode_hex
from eth_utils import function_signature_to_4byte_selector as fourbyte

from y.contracts import Contract, proxy_implementation
from y.convert import to_address, to_address_async
from y.datatypes import Address, AddressOrContract, Block
from y.exceptions import (
    CalldataPreparationError,
    ContractNotVerified,
    NonStandardERC20,
    NoProxyImplementation,
    call_reverted,
)
from y.networks import Network
from y.utils.logging import yLazyLogger

logger = logging.getLogger(__name__)

"""
We use raw calls for commonly used functions because its much faster than using brownie Contracts
"""


# yLazyLogger(logger)
@a_sync.a_sync(cache_type="memory")
async def _cached_call_fn(
    func: Callable,
    contract_address: AddressOrContract,
    # Only supports one required arg besides contract_address for now
    block: Optional[Block],
    required_arg=None,
) -> Any:
    if required_arg is None:
        return await func(contract_address, block=block)
    else:
        return await func(contract_address, required_arg, block=block)


@a_sync.a_sync(default="sync")
async def decimals(
    contract_address: AddressOrContract,
    block: Optional[Block] = None,
    return_None_on_failure: bool = False,
) -> int:
    if block is None or return_None_on_failure:
        return await _decimals(
            contract_address, block=block, return_None_on_failure=return_None_on_failure
        )
    else:
        return await _cached_call_fn(_decimals, contract_address, block)


@a_sync.a_sync(default="sync", cache_type="memory")
async def _decimals(
    contract_address: AddressOrContract,
    block: Optional[Block] = None,
    return_None_on_failure: bool = False,
) -> Optional[int]:

    decimals = None

    # method 1
    # NOTE: this will almost always work, you will rarely proceed to further methods
    try:
        decimals = await raw_call(
            contract_address,
            "decimals()",
            block=block,
            output="int",
            return_None_on_failure=True,
            sync=False,
        )
    except (OverflowError, ValueError):
        # OverflowError means the call didn't revert, but we can't decode it correctly
        # the contract might not comply with standards, so we can possibly fetch
        # using the verified non standard abi as a fallback
        # ValueError means the call failed for some other reason, but let's try this anyway
        try:
            contract = await Contract.coroutine(contract_address)
            decimals = await contract.decimals.coroutine(block_identifier=block)
        except ContractNotVerified:
            pass
        except AttributeError as e:
            if "has no attribute 'decimals'" not in str(e):
                raise
            # we got a response from the chain but brownie can't find `DECIMALS` method,
            # maybe our cached contract definition is messed up. let's repull it
            with contextlib.suppress(AttributeError):
                decimals = brownie.Contract.from_explorer(contract_address).decimals(
                    block_identifier=block
                )

    if decimals is not None:
        return decimals

    # method 2
    try:
        decimals = await raw_call(
            contract_address,
            "DECIMALS()",
            block=block,
            output="int",
            return_None_on_failure=True,
            sync=False,
        )
    except (OverflowError, ValueError):
        # OverflowError means the call didn't revert, but we can't decode it correctly
        # the contract might not comply with standards, so we can possibly fetch DECIMALS
        # using the verified non standard abi as a fallback
        # ValueError means the call failed for some other reason, but let's try this anyway
        try:
            contract = await Contract.coroutine(contract_address)
            decimals = await contract.DECIMALS.coroutine(block_identifier=block)
        except ContractNotVerified:
            pass
        except AttributeError as e:
            if "has no attribute 'DECIMALS'" not in str(e):
                raise
            # we got a response from the chain but brownie can't find `DECIMALS` method,
            # maybe our cached contract definition is messed up. let's repull it
            with contextlib.suppress(AttributeError):
                decimals = brownie.Contract.from_explorer(contract_address).DECIMALS(
                    block_identifier=block
                )

    if decimals is not None:
        return decimals

    # method 3
    try:
        decimals = await raw_call(
            contract_address,
            "getDecimals()",
            block=block,
            output="int",
            return_None_on_failure=True,
            sync=False,
        )
    except (OverflowError, ValueError):
        # OverflowError means the call didn't revert, but we can't decode it correctly
        # the contract might not comply with standards, so we can possibly fetch DECIMALS
        # using the verified non standard abi as a fallback
        # ValueError means the call failed for some other reason, but let's try this anyway
        try:
            contract = await Contract.coroutine(contract_address)
            decimals = await contract.getDecimals.coroutine(block_identifier=block)
        except ContractNotVerified:
            pass
        except AttributeError as e:
            if "has no attribute 'getDecimals'" not in str(e):
                raise
            # we got a response from the chain but brownie can't find `DECIMALS` method,
            # maybe our cached contract definition is messed up. let's repull it
            with contextlib.suppress(AttributeError):
                decimals = brownie.Contract.from_explorer(contract_address).getDecimals(
                    block_identifier=block
                )

    if decimals is not None:
        return decimals

    # we've failed to fetch
    if return_None_on_failure:
        return None

    if await proxy_implementation(contract_address, block) == ZERO_ADDRESS:
        raise NoProxyImplementation(
            f"""
            Contract {contract_address} is a proxy contract, and had no implementation at block {block}."""
        )

    raise NonStandardERC20(
        f"""
        Unable to fetch `decimals` for {contract_address} on {Network.printable()}
        If the contract is verified, please check to see if it has a strangely named
        `decimals` method and create an issue on https://github.com/BobTheBuidler/ypricemagic
        with the contract address and correct method name so we can keep things going smoothly :)"""
    )


@a_sync.a_sync(default="sync")
async def _totalSupply(
    contract_address: AddressOrContract,
    block: Optional[Block] = None,
    return_None_on_failure: bool = False,
) -> Optional[int]:

    total_supply = None

    try:
        total_supply = await raw_call(
            contract_address,
            "totalSupply()",
            block=block,
            output="int",
            return_None_on_failure=True,
            sync=False,
        )
    except OverflowError:
        # OverflowError means the call didn't revert, but we can't decode it correctly
        # the contract might not comply with standards, so we can possibly fetch totalSupply
        # using the verified non standard abi as a fallback
        try:
            contract = await Contract.coroutine(contract_address)
            total_supply = await contract.totalSupply.coroutine(block_identifier=block)
        except ContractNotVerified:
            pass
        except AttributeError as e:
            if "has no attribute 'totalSupply'" not in str(e):
                raise
            # we got a response from the chain but brownie can't find `totalSupply` method,
            # maybe our cached contract definition is messed up. let's repull it
            with contextlib.suppress(AttributeError):
                total_supply = brownie.Contract.from_explorer(
                    contract_address
                ).totalSupply(block_identifier=block)

    if total_supply is not None:
        return total_supply

    if return_None_on_failure:
        return None
    raise NonStandardERC20(
        f"""
        Unable to fetch `totalSupply` for {contract_address} on {Network.printable()}
        If the contract is verified, please check to see if it has a strangely named
        `totalSupply` method and create an issue on https://github.com/BobTheBuidler/ypricemagic
        with the contract address and correct method name so we can keep things going smoothly :)"""
    )


@a_sync.a_sync(default="sync")
async def balanceOf(
    call_address: AddressOrContract,
    input_address: AddressOrContract,
    block: Optional[Block] = None,
    return_None_on_failure: bool = False,
) -> Optional[int]:

    # method 1
    # NOTE: this will almost always work, you will rarely proceed to further methods
    try:
        balance = await raw_call(
            call_address,
            "balanceOf(address)",
            block=block,
            inputs=input_address,
            output="int",
            return_None_on_failure=True,
            sync=False,
        )
    except OverflowError:
        # OverflowError means the call didn't revert, but we can't decode it correctly
        # the contract might not comply with standards, so we can possibly fetch balanceOf
        # using the verified non standard abi as a fallback
        try:
            contract = await Contract.coroutine(call_address)
            return await contract.balanceOf.coroutine(
                input_address, block_identifier=block
            )
        except AttributeError as e:
            if "has no attribute 'balanceOf'" not in str(e):
                raise
            # we got a response from the chain but brownie can't find `balanceOf` method,
            # maybe our cached contract definition is messed up. let's repull it
            balance = brownie.Contract.from_explorer(call_address).balanceOf(
                input_address, block_identifier=block
            )

    if balance is not None:
        return balance

    # we've failed to fetch
    if return_None_on_failure:
        return None
    raise NonStandardERC20(
        f"""
        Unable to fetch `balanceOf` for token: {call_address} holder: {input_address} on {Network.printable()}
        If the contract is verified, please check to see if it has a strangely named
        `totalSupply` method and create an issue on https://github.com/BobTheBuidler/ypricemagic
        with the contract address and correct function name so we can keep things going smoothly :)"""
    )


# yLazyLogger(logger)
async def _balanceOfReadable(
    call_address: AddressOrContract,
    input_address: AddressOrContract,
    block: Optional[Block] = None,
    return_None_on_failure: bool = False,
) -> Optional[float]:

    balance, decimals = await cgather(
        balanceOf(
            call_address,
            input_address,
            block=block,
            return_None_on_failure=return_None_on_failure,
            sync=False,
        ),
        _decimals(
            call_address, block=block, return_None_on_failure=return_None_on_failure
        ),
    )
    if balance is not None and decimals is not None:
        return balance / 10**decimals

    # we've failed to fetch
    if return_None_on_failure:
        return None
    else:
        raise NonStandardERC20(
            f"""Unable to fetch `balanceOfReadable` for
        token: {call_address} holder: {input_address} on {Network.printable()}
        balanceOf: {balance} decimals: {decimals}
        If the contract is verified, please check to see if it has a strangely named `balanceOf` or
        `decimals` method and create an issue on https://github.com/BobTheBuidler/ypricemagic
        with the contract address and correct function name so we can keep things going smoothly :)"""
        )


@a_sync.a_sync(default="sync")
async def raw_call(
    contract_address: AddressOrContract,
    method: str,
    block: Optional[Block] = None,
    inputs=None,
    output: str = None,
    return_None_on_failure: bool = False,
) -> Optional[Any]:
    """
    Call a contract with only address and method. Bypasses brownie Contract object formation to save time.

    This function allows for direct interaction with a contract by preparing and sending
    the call data without creating a full contract object. It supports various input types
    and can handle multiple inputs.

    Args:
        contract_address: The address of the contract.
        method: The method signature as a string (e.g., "transfer(address,uint256)").
        block: The block number at which to make the call. Defaults to the latest block.
        inputs: The input data for the method. Can be None, bytes, int, str, Address,
                EthAddress, brownie.Contract, or Contract.
        output: The expected output type. Options are "address", "int", "str".
        return_None_on_failure: If True, return None if the call fails. Default False.

    Examples:
        >>> await raw_call("0xTokenAddress", "balanceOf(address)", inputs="0xHolderAddress")
        1000000000000000000

        >>> await raw_call("0xTokenAddress", "decimals()")
        18

    Raises:
        ValueError: If the call fails and `return_None_on_failure` is False.
        TypeError: If an invalid output type is specified.

    See Also:
        - :func:`prepare_data` for preparing the call data.
        - :func:`prepare_input` for preparing individual inputs.
    """

    if type(contract_address) != str:
        contract_address = str(contract_address)

    data = {
        "to": await to_address_async(contract_address),
        "data": prepare_data(method, inputs),
    }

    try:
        response = await dank_mids.eth.call(data, block_identifier=block)
    except ValueError as e:
        if return_None_on_failure and (call_reverted(e) or "invalid opcode" in str(e)):
            return None
        raise

    try:
        if output is None:
            return response
        elif output == "address" and response.hex() == "0x":
            return ZERO_ADDRESS
        elif output == "address":
            return await to_address_async(f"0x{response.hex()[-40:]}")
        elif output in [int, "int", "uint", "uint256"]:
            return convert.to_int(response)
        elif output in [str, "str"]:
            return convert.to_string(response).replace("\x00", "").strip()
    except OverflowError as e:
        if "is outside allowable range for uint256" in str(e):
            raise OverflowError(
                f"0x{response.hex()} is outside allowable range for uint256"
            ) from e
        raise
    else:
        raise TypeError(
            'Invalid output type, please select from ["str","int","address"]'
        )


# yLazyLogger(logger)
def prepare_data(
    method,
    inputs=Union[
        None, bytes, int, str, Address, EthAddress, brownie.Contract, Contract
    ],
) -> str:
    """
    Prepare data for a raw contract call by encoding the method signature and input data.

    This function takes a method signature and input data, and returns a hexadecimal string
    that can be used as the data field in a raw contract call.

    Args:
        method: The method signature as a string (e.g., "transfer(address,uint256)").
        inputs: The input data for the method. Can be None, bytes, int, str, Address,
                EthAddress, brownie.Contract, or Contract.

    Returns:
        A hexadecimal string representing the encoded method call data.

    Raises:
        CalldataPreparationError: If the input type is not supported.

    Note:
        - The method signature is encoded to its 4-byte function selector.
        - If inputs is None, only the method selector is returned.
        - For other input types, the input is prepared and appended to the method selector.

    Examples:
        >>> prepare_data("transfer(address,uint256)", inputs=("0xRecipientAddress", 1000))
        '0xa9059cbb000000000000000000000000RecipientAddress00000000000000000000000000000000000003e8'

        >>> prepare_data("decimals()")
        '0x313ce567'

    See Also:
        - :func:`raw_call` for making the contract call.
        - :func:`prepare_input` for preparing individual inputs.
    """
    method = encode_hex(fourbyte(method))

    if inputs is None:
        return method

    elif type(inputs) in [
        bytes,
        int,
        str,
        Address,
        EthAddress,
        brownie.Contract,
        Contract,
    ]:
        return method + prepare_input(inputs)

    raise CalldataPreparationError(
        f"""
        Supported types are: Union[None, bytes, int, str, Address, EthAddress, brownie.Contract, y.Contract]
        You passed {type(inputs)} {inputs}"""
    )

    # these don't work yet, wip
    """
    elif type(inputs) in (Set,List,Tuple):
        # this doesn't work right now
        inputs = str(concat([method,*map(prepare_input, inputs)]))
        logger.warning(inputs)
        return encode_hex(inputs)
    elif type(inputs) == Dict:
        # this doesn't work right now
        inputs = str(concat([method,*map(prepare_input, inputs.values())]))
        logger.warning(inputs)
        return encode_hex(inputs)
    """


# yLazyLogger(logger)
def prepare_input(
    input: Union[
        bytes,  # for bytes input
        int,  # for int input
        # for address input
        Union[str, Address, EthAddress, brownie.Contract, Contract],
    ],
) -> str:
    """
    Prepare input data for a raw contract call by encoding it to a hexadecimal string.

    This function takes various input types and converts them to a hexadecimal string
    that can be used as part of the data field in a raw contract call.

    Args:
        input: The input data to be prepared. Can be bytes, int, str, Address,
               EthAddress, brownie.Contract, or Contract.

    Returns:
        A hexadecimal string representing the encoded input data.

    Raises:
        CalldataPreparationError: If the input type is not supported.

    Note:
        - Bytes input is converted directly to its hexadecimal representation.
        - Integer input is converted to bytes and then to hexadecimal.
        - String, Address, EthAddress, brownie.Contract, and Contract inputs are
          assumed to be addresses and are padded to 32 bytes.

    Examples:
        >>> prepare_input("0xRecipientAddress")
        '000000000000000000000000RecipientAddress'

        >>> prepare_input(1000)
        '00000000000000000000000000000000000000000000000000000000000003e8'

    See Also:
        - :func:`prepare_data` for preparing the call data.
        - :func:`raw_call` for making the contract call.
    """
    input_type = type(input)

    if input_type == bytes:
        return input.hex()

    if input_type == int:
        return convert.to_bytes(input).hex()

    # we can't process actual strings so we can assume that any string input is an address. regular strings will fail
    if input_type in [str, Address, EthAddress, brownie.Contract, Contract]:
        return f"000000000000000000000000{to_address(input)[2:]}"

    raise CalldataPreparationError(
        f"""
        Supported input types are
        uint: int, 
        address: Union[str, Address, brownie.Contract, y.Contract]
        you passed input: {input} type: {input_type}
        """
    )
