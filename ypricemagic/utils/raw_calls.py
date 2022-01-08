from brownie import convert, web3
from eth_utils import encode_hex
from eth_utils import function_signature_to_4byte_selector as fourbyte


def _decimals(contract_address, block=None):
    data = raw_call(contract_address, "decimals()", block=block)
    return convert.to_int(data)


def _symbol(contract_address, block=None):
    data = raw_call(contract_address, "symbol()", block=block)
    return convert.to_string(data) 


def _totalSupply(contract_address, block=None):
    data = raw_call(contract_address, "totalSupply()", block=block)
    return convert.to_int(data)


def _totalSupplyReadable(contract_address, block=None):
    return _totalSupply(contract_address,block) / 10 ** _decimals(contract_address,block)


def raw_call(contract_address: str, method: str, block=None):
    address = convert.to_address(contract_address)
    data = {'to': address,'data': encode_hex(fourbyte(method))}
    return web3.eth.call(data,block_identifier=block)
