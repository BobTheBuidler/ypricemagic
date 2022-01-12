from typing import Dict, List, Set, Tuple
from brownie import convert, web3
from eth_utils import encode_hex
from eth_utils import function_signature_to_4byte_selector as fourbyte
from toolz.itertoolz import concat
from ypricemagic import Contract


def _decimals(contract_address, block=None):
    try: return convert.to_int(raw_call(contract_address, "decimals()", block=block))
    except OverflowError: return Contract(contract_address).decimals(block_identifier=block)


def _symbol(contract_address, block=None):
    data = raw_call(contract_address, "symbol()", block=block)
    return convert.to_string(data) 


def _totalSupply(contract_address, block=None):
    try: return convert.to_int(raw_call(contract_address, "totalSupply()", block=block))
    except OverflowError: return Contract(contract_address).totalSupply(block_identifier=block)


def _totalSupplyReadable(contract_address, block=None):
    return _totalSupply(contract_address,block) / 10 ** _decimals(contract_address,block)


def _balanceOf(call_address, input_address, block=None):
    data = raw_call(call_address, "balanceOf(address)", block=block, inputs=input_address)
    return convert.to_int(data)


def _balanceOfReadable(call_address, input_address, block=None):
    return _balanceOf(call_address, input_address, block=block) / 10 ** _decimals(call_address, block)


def raw_call(contract_address: str, method: str, block=None, inputs=None, output:str=None):
    '''
    call a contract with only address and method.
    only works with 1 input, ie `balanceOf(address)`
    '''
    data = {'to': convert.to_address(contract_address),'data': prepare_data(method,inputs)}
    response = web3.eth.call(data,block_identifier=block)
    if output is None: return response
    elif output == 'address': return convert.to_address(f'0x{response.hex()[-40:]}')
    elif output in ['int','uint','uint256']: return convert.to_int(response)

def prepare_data(method, inputs=None):
    method = fourbyte(method)
    if inputs is None:
        return encode_hex(method)
    elif type(inputs) in [str,int,bytes]:
        return encode_hex(concat(method,prepare_input(inputs)))
    elif type(inputs) in (Set,List,Tuple):
        return encode_hex(concat(method,*[prepare_input(_) for _ in inputs]))
    elif type(inputs) == Dict:
        return encode_hex(concat(method,*[prepare_input(_) for _ in inputs.values()]))
    else:
        raise ValueError(f'Unsupported input type. Supported types are: str, int, bytes, Set[str,int,bytes], List[str,int,bytes], Tuple[str,int,bytes], Dict[Any:[str,int,bytes]]')

def prepare_input(input):
    try: return '000000000000000000000000' + convert.to_address(input)[2:]
    except: raise 
    
