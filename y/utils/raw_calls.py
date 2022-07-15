import logging
from typing import Any, Callable, Optional, Union

import brownie
from async_lru import alru_cache
from brownie import ZERO_ADDRESS, convert, web3
from brownie.convert.datatypes import EthAddress
from eth_utils import encode_hex
from eth_utils import function_signature_to_4byte_selector as fourbyte
from y.contracts import Contract, proxy_implementation
from y.datatypes import Address, AddressOrContract, Block
from y.exceptions import (CalldataPreparationError, ContractNotVerified,
                          NonStandardERC20, NoProxyImplementation,
                          call_reverted)
from y.networks import Network
from y.utils.cache import memory
from y.utils.dank_mids import dank_w3
from y.utils.logging import yLazyLogger

from multicall.utils import await_awaitable, gather

logger = logging.getLogger(__name__)

"""
We use raw calls for commonly used functions because its much faster than using brownie Contracts
"""

@yLazyLogger(logger)
@alru_cache(maxsize=None)
async def _cached_call_fn(
    func: Callable,
    contract_address: AddressOrContract, 
    # Only supports one required arg besides contract_address for now
    block: Optional[Block], 
    required_arg = None,
    ) -> Any:
    if required_arg is None:
        return await func(contract_address, block=block)
    else:
        return await func(contract_address, required_arg, block=block)


@yLazyLogger(logger)
async def decimals(
    contract_address: AddressOrContract, 
    block: Optional[Block] = None, 
    return_None_on_failure: bool = False
    ) -> int:
    if block is None or return_None_on_failure is True: 
        return await _decimals(contract_address, block=block, return_None_on_failure=return_None_on_failure)
    else:
        return await _cached_call_fn(_decimals,contract_address,block)


@yLazyLogger(logger)
@alru_cache(maxsize=None)
async def _decimals(
    contract_address: AddressOrContract, 
    block: Optional[Block] = None, 
    return_None_on_failure: bool = False
    ) -> Optional[int]:

    decimals = None

    # method 1
    # NOTE: this will almost always work, you will rarely proceed to further methods
    try: decimals = await raw_call_async(contract_address, "decimals()", block=block, output='int', return_None_on_failure=True)
    except OverflowError:
        # OverflowError means the call didn't revert, but we can't decode it correctly
        # the contract might not comply with standards, so we can possibly fetch 
        # using the verified non standard abi as a fallback
        try: decimals = await Contract(contract_address).decimals.coroutine(block_identifier=block)
        except ContractNotVerified:
            pass
        except AttributeError as e:
            if "has no attribute 'decimals'" not in str(e):
                raise
            # we got a response from the chain but brownie can't find `DECIMALS` method, 
            # maybe our cached contract definition is messed up. let's repull it
            decimals = brownie.Contract.from_explorer(contract_address).decimals(block_identifier=block)

    if decimals is not None:
        return decimals

    # method 2
    try: decimals = await raw_call_async(contract_address, "DECIMALS()", block=block, output='int', return_None_on_failure=True)
    except OverflowError: 
        # OverflowError means the call didn't revert, but we can't decode it correctly
        # the contract might not comply with standards, so we can possibly fetch DECIMALS 
        # using the verified non standard abi as a fallback
        try: decimals = await Contract(contract_address).DECIMALS.coroutine(block_identifier=block)
        except ContractNotVerified:
            pass
        except AttributeError as e:
            if "has no attribute 'DECIMALS'" not in str(e):
                raise
            # we got a response from the chain but brownie can't find `DECIMALS` method, 
            # maybe our cached contract definition is messed up. let's repull it
            decimals = brownie.Contract.from_explorer(contract_address).DECIMALS(block_identifier=block)
                
    if decimals is not None:
        return decimals

    # method 3
    try: decimals = await raw_call_async(contract_address, "getDecimals()", block=block, output='int', return_None_on_failure=True)
    except OverflowError: 
        # OverflowError means the call didn't revert, but we can't decode it correctly
        # the contract might not comply with standards, so we can possibly fetch DECIMALS 
        # using the verified non standard abi as a fallback
        try: decimals = await Contract(contract_address).getDecimals.coroutine(block_identifier=block)
        except ContractNotVerified:
            pass
        except AttributeError as e:
            if "has no attribute 'getDecimals'" not in str(e):
                raise
            # we got a response from the chain but brownie can't find `DECIMALS` method, 
            # maybe our cached contract definition is messed up. let's repull it
            decimals = brownie.Contract.from_explorer(contract_address).getDecimals(block_identifier=block)
                
    if decimals is not None:
        return decimals

    # we've failed to fetch
    if return_None_on_failure:
        return None

    if await proxy_implementation(contract_address, block) == ZERO_ADDRESS:
        raise NoProxyImplementation(f"""
            Contract {contract_address} is a proxy contract, and had no implementation at block {block}.""")

    raise NonStandardERC20(f'''
        Unable to fetch `decimals` for {contract_address} on {Network.printable()}
        If the contract is verified, please check to see if it has a strangely named
        `decimals` method and create an issue on https://github.com/BobTheBuidler/ypricemagic
        with the contract address and correct method name so we can keep things going smoothly :)''')


@yLazyLogger(logger)
async def _totalSupply(
    contract_address: AddressOrContract, 
    block: Optional[Block] = None,
    return_None_on_failure: bool = False # TODO: implement this kwarg
    ) -> Optional[int]:

    try: total_supply = await raw_call_async(contract_address, "totalSupply()", block=block, output='int', return_None_on_failure=True)
    except OverflowError:
        # OverflowError means the call didn't revert, but we can't decode it correctly
        # the contract might not comply with standards, so we can possibly fetch totalSupply 
        # using the verified non standard abi as a fallback
        try:
            total_supply = await Contract(contract_address).totalSupply.coroutine(block_identifier=block)
        except AttributeError as e:
            if "has no attribute 'totalSupply'" not in str(e):
                raise
            # we got a response from the chain but brownie can't find `totalSupply` method, 
            # maybe our cached contract definition is messed up. let's repull it
            total_supply = brownie.Contract.from_explorer(contract_address).totalSupply(block_identifier=block)

    if total_supply is not None:
        return total_supply

    if return_None_on_failure:
        return None
    raise NonStandardERC20(f'''
        Unable to fetch `totalSupply` for {contract_address} on {Network.printable()}
        If the contract is verified, please check to see if it has a strangely named
        `totalSupply` method and create an issue on https://github.com/BobTheBuidler/ypricemagic
        with the contract address and correct method name so we can keep things going smoothly :)''')


@yLazyLogger(logger)
async def _totalSupplyReadable(
    contract_address: AddressOrContract, 
    block: Optional[Block] = None,
    return_None_on_failure: bool = False
    ) -> Optional[float]:

    total_supply = _totalSupply(contract_address, block=block, return_None_on_failure=return_None_on_failure)
    decimals = _decimals(contract_address, block=block, return_None_on_failure=return_None_on_failure)
    total_supply, decimals = await gather([total_supply, decimals])

    if total_supply is not None and decimals is not None:
        return total_supply / 10 ** decimals

    if total_supply is None and decimals is None and return_None_on_failure:
        return None

    raise NonStandardERC20(f'''
        Unable to fetch `totalSupplyReadable` for {contract_address} on {Network.printable()}
        totalSupply: {total_supply} decimals: {decimals}
        If the contract is verified, please check to see if it has a strangely named `totalSupply` or
        `decimals` method and create an issue on https://github.com/BobTheBuidler/ypricemagic
        with the contract address and correct function name so we can keep things going smoothly :)''')

def balanceOf(
    contract_address: AddressOrContract, 
    address: Address, 
    block: Optional[Block] = None,
    return_None_on_failure: bool = False
    ) -> Optional[int]:
    return await_awaitable(balanceOf_async(contract_address, address, block=block, return_None_on_failure=return_None_on_failure))

@yLazyLogger(logger)
async def balanceOf_async(
    call_address: AddressOrContract, 
    input_address: AddressOrContract, 
    block: Optional[Block] = None,
    return_None_on_failure: bool = False
    ) -> Optional[int]:

    # method 1
    # NOTE: this will almost always work, you will rarely proceed to further methods
    try:
        balance = await raw_call_async(call_address, "balanceOf(address)", block=block, inputs=input_address, output='int', return_None_on_failure=True)
    except OverflowError:
        # OverflowError means the call didn't revert, but we can't decode it correctly
        # the contract might not comply with standards, so we can possibly fetch balanceOf 
        # using the verified non standard abi as a fallback
        try: return await Contract(call_address).balanceOf.coroutine(input_address, block_identifier=block)
        except AttributeError as e:
            if "has no attribute 'balanceOf'" not in str(e):
                raise
            # we got a response from the chain but brownie can't find `balanceOf` method, 
            # maybe our cached contract definition is messed up. let's repull it
            balance = brownie.Contract.from_explorer(call_address).balanceOf(input_address, block_identifier=block)
    
    if balance is not None:
        return balance

    # we've failed to fetch
    if return_None_on_failure:
        return None
    raise NonStandardERC20(f'''
        Unable to fetch `balanceOf` for token: {call_address} holder: {input_address} on {Network.printable()}
        If the contract is verified, please check to see if it has a strangely named
        `totalSupply` method and create an issue on https://github.com/BobTheBuidler/ypricemagic
        with the contract address and correct function name so we can keep things going smoothly :)''')


@yLazyLogger(logger)
async def _balanceOfReadable(
    call_address: AddressOrContract, 
    input_address: AddressOrContract, 
    block: Optional[Block] = None,
    return_None_on_failure: bool = False
    ) -> Optional[float]:

    # TODO _balanceOf return_None_on_failure
    balance = balanceOf_async(call_address, input_address, block=block, return_None_on_failure=return_None_on_failure)
    decimals = _decimals(call_address, block=block, return_None_on_failure=return_None_on_failure)
    balance, decimals = await gather([balance, decimals])
    if balance is not None and decimals is not None:
        return balance / 10 ** decimals

    # we've failed to fetch
    if return_None_on_failure:
        return None
    else:
        raise NonStandardERC20(
        f'''Unable to fetch `balanceOfReadable` for
        token: {call_address} holder: {input_address} on {Network.printable()}
        balanceOf: {balance} decimals: {decimals}
        If the contract is verified, please check to see if it has a strangely named `balanceOf` or
        `decimals` method and create an issue on https://github.com/BobTheBuidler/ypricemagic
        with the contract address and correct function name so we can keep things going smoothly :)''')


@yLazyLogger(logger)
def raw_call(
    contract_address: AddressOrContract, 
    method: str, 
    block: Optional[Block] = None, 
    inputs = None, 
    output: str = None,
    return_None_on_failure: bool = False
    ) -> Optional[Any]:

    if type(contract_address) != str:
        contract_address = str(contract_address)

    data = {'to': convert.to_address(contract_address),'data': prepare_data(method,inputs)}

    try: response = web3.eth.call(data,block_identifier=block)
    except ValueError as e:
        if return_None_on_failure is False:                 raise
        if call_reverted(e):                                return None
        if 'invalid opcode' in str(e):                      return None
        else:                                               raise
    
    if output is None:                                      return response
    elif output == 'address' and response.hex() == '0x':    return ZERO_ADDRESS
    elif output == 'address':                               return convert.to_address(f'0x{response.hex()[-40:]}')
    elif output in [int, 'int','uint','uint256']:           return convert.to_int(response)
    elif output in [str, 'str']:                            return convert.to_string(response).replace('\x00','').strip()

    else: raise TypeError('Invalid output type, please select from ["str","int","address"]')


@yLazyLogger(logger)
async def raw_call_async(
    contract_address: AddressOrContract, 
    method: str, 
    block: Optional[Block] = None, 
    inputs = None, 
    output: str = None,
    return_None_on_failure: bool = False
    ) -> Optional[Any]:
    '''
    call a contract with only address and method. Bypasses brownie Contract object formation to save time
    only works with 1 input, ie `balanceOf(address)` or `getPoolInfo(uint256)`
    '''

    if type(contract_address) != str:
        contract_address = str(contract_address)

    data = {'to': convert.to_address(contract_address),'data': prepare_data(method,inputs)}

    try: response = await dank_w3.eth.call(data,block_identifier=block)
    except ValueError as e:
        if return_None_on_failure is False:                 raise
        if call_reverted(e):                                return None
        if 'invalid opcode' in str(e):                      return None
        else:                                               raise
    
    if output is None:                                      return response
    elif output == 'address' and response.hex() == '0x':    return ZERO_ADDRESS
    elif output == 'address':                               return convert.to_address(f'0x{response.hex()[-40:]}')
    elif output in [int, 'int','uint','uint256']:           return convert.to_int(response)
    elif output in [str, 'str']:                            return convert.to_string(response).replace('\x00','').strip()

    else: raise TypeError('Invalid output type, please select from ["str","int","address"]')


@yLazyLogger(logger)
def prepare_data(
    method, 
    inputs = Union[None, bytes, int, str, Address, EthAddress, brownie.Contract, Contract]
    ) -> str:
    method = encode_hex(fourbyte(method))

    if inputs is None:
        return method

    elif type(inputs) in [bytes, int, str, Address, EthAddress, brownie.Contract, Contract]:
        return method + prepare_input(inputs)
    
    raise CalldataPreparationError(f'''
        Supported types are: Union[None, bytes, int, str, Address, EthAddress, brownie.Contract, y.Contract]
        You passed {type(inputs)} {inputs}''')
    
    # these don't work yet, wip
    '''
    elif type(inputs) in (Set,List,Tuple):
        # this doesn't work right now
        inputs = str(concat([method,*[prepare_input(_) for _ in inputs]]))
        logger.warning(inputs)
        return encode_hex(inputs)
    elif type(inputs) == Dict:
        # this doesn't work right now
        inputs = str(concat([method,*[prepare_input(_) for _ in inputs.values()]]))
        logger.warning(inputs)
        return encode_hex(inputs)
    '''


@yLazyLogger(logger)
def prepare_input(
    input: Union[
        bytes, # for bytes input
        int, # for int input
        Union[str, Address, EthAddress, brownie.Contract, Contract] # for address input
        ]
    ) -> str:
    
    input_type = type(input)

    if input_type == bytes:
        return input.hex()

    if input_type == int:
        return convert.to_bytes(input).hex()

    # we can't process actual strings so we can assume that any string input is an address. regular strings will fail
    if input_type in [str, Address, EthAddress, brownie.Contract, Contract]:
        return '000000000000000000000000' + convert.to_address(input)[2:]
    
    raise CalldataPreparationError(f'''
        Supported input types are
        uint: int, 
        address: Union[str, Address, brownie.Contract, y.Contract]
        you passed input: {input} type: {input_type}
        ''')
