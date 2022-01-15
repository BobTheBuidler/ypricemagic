from collections import defaultdict
from itertools import count, product
from operator import itemgetter
from typing import Any, List, Sequence, Tuple, Union

import brownie
import requests
from brownie import chain, convert, web3
from brownie.convert.datatypes import EthAddress
from eth_abi.exceptions import InsufficientDataBytes
from eth_typing.evm import Address, BlockNumber
from web3.exceptions import CannotHandleRequest
from y.contracts import contract_creation_block, Contract
from y.networks import Network
from ypricemagic.utils.raw_calls import _decimals, _totalSupply

from multicall import Call, Multicall

SUPPORTED_INPUT_TYPES = str, Address, EthAddress, brownie.Contract, Contract

MULTICALL2 = {
    Network.Mainnet: "0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696",
    Network.BinanceSmartChain: "0xfF6FD90A470Aaa0c1B8A54681746b07AcdFedc9B",
    Network.Polygon: "0xc8E51042792d7405184DfCa245F2d27B94D013b6",
    Network.Fantom: "0xBAD2B082e2212DE4B065F636CA4e5e0717623d18",
}.get(chain.id, None)

multicall = None
multicall2 = Contract(MULTICALL2) if MULTICALL2 else None

# the address doesn't matter, it just needs to have code
code = "0x608060405234801561001057600080fd5b50600436106100b45760003560e01c806372425d9d1161007157806372425d9d1461013d57806386d516e814610145578063a8b0574e1461014d578063bce38bd714610162578063c3077fa914610182578063ee82ac5e14610195576100b4565b80630f28c97d146100b9578063252dba42146100d757806327e86d6e146100f8578063399542e91461010057806342cbb15c146101225780634d2301cc1461012a575b600080fd5b6100c16101a8565b6040516100ce919061083b565b60405180910390f35b6100ea6100e53660046106bb565b6101ac565b6040516100ce9291906108ba565b6100c1610340565b61011361010e3660046106f6565b610353565b6040516100ce93929190610922565b6100c161036b565b6100c161013836600461069a565b61036f565b6100c161037c565b6100c1610380565b610155610384565b6040516100ce9190610814565b6101756101703660046106f6565b610388565b6040516100ce9190610828565b6101136101903660046106bb565b610533565b6100c16101a3366004610748565b610550565b4290565b8051439060609067ffffffffffffffff8111156101d957634e487b7160e01b600052604160045260246000fd5b60405190808252806020026020018201604052801561020c57816020015b60608152602001906001900390816101f75790505b50905060005b835181101561033a5760008085838151811061023e57634e487b7160e01b600052603260045260246000fd5b6020026020010151600001516001600160a01b031686848151811061027357634e487b7160e01b600052603260045260246000fd5b60200260200101516020015160405161028c91906107f8565b6000604051808303816000865af19150503d80600081146102c9576040519150601f19603f3d011682016040523d82523d6000602084013e6102ce565b606091505b5091509150816102f95760405162461bcd60e51b81526004016102f090610885565b60405180910390fd5b8084848151811061031a57634e487b7160e01b600052603260045260246000fd5b602002602001018190525050508080610332906109c2565b915050610212565b50915091565b600061034d60014361097b565b40905090565b43804060606103628585610388565b90509250925092565b4390565b6001600160a01b03163190565b4490565b4590565b4190565b6060815167ffffffffffffffff8111156103b257634e487b7160e01b600052604160045260246000fd5b6040519080825280602002602001820160405280156103eb57816020015b6103d8610554565b8152602001906001900390816103d05790505b50905060005b825181101561052c5760008084838151811061041d57634e487b7160e01b600052603260045260246000fd5b6020026020010151600001516001600160a01b031685848151811061045257634e487b7160e01b600052603260045260246000fd5b60200260200101516020015160405161046b91906107f8565b6000604051808303816000865af19150503d80600081146104a8576040519150601f19603f3d011682016040523d82523d6000602084013e6104ad565b606091505b509150915085156104d557816104d55760405162461bcd60e51b81526004016102f090610844565b604051806040016040528083151581526020018281525084848151811061050c57634e487b7160e01b600052603260045260246000fd5b602002602001018190525050508080610524906109c2565b9150506103f1565b5092915050565b6000806060610543600185610353565b9196909550909350915050565b4090565b60408051808201909152600081526060602082015290565b80356001600160a01b038116811461058357600080fd5b919050565b600082601f830112610598578081fd5b8135602067ffffffffffffffff808311156105b5576105b56109f3565b6105c2828385020161094a565b83815282810190868401865b8681101561068c57813589016040601f198181848f030112156105ef578a8bfd5b6105f88261094a565b6106038a850161056c565b81528284013589811115610615578c8dfd5b8085019450508d603f850112610629578b8cfd5b898401358981111561063d5761063d6109f3565b61064d8b84601f8401160161094a565b92508083528e84828701011115610662578c8dfd5b808486018c85013782018a018c9052808a01919091528652505092850192908501906001016105ce565b509098975050505050505050565b6000602082840312156106ab578081fd5b6106b48261056c565b9392505050565b6000602082840312156106cc578081fd5b813567ffffffffffffffff8111156106e2578182fd5b6106ee84828501610588565b949350505050565b60008060408385031215610708578081fd5b82358015158114610717578182fd5b9150602083013567ffffffffffffffff811115610732578182fd5b61073e85828601610588565b9150509250929050565b600060208284031215610759578081fd5b5035919050565b60008282518085526020808601955080818302840101818601855b848110156107bf57858303601f19018952815180511515845284015160408585018190526107ab818601836107cc565b9a86019a945050509083019060010161077b565b5090979650505050505050565b600081518084526107e4816020860160208601610992565b601f01601f19169290920160200192915050565b6000825161080a818460208701610992565b9190910192915050565b6001600160a01b0391909116815260200190565b6000602082526106b46020830184610760565b90815260200190565b60208082526021908201527f4d756c746963616c6c32206167677265676174653a2063616c6c206661696c656040820152601960fa1b606082015260800190565b6020808252818101527f4d756c746963616c6c206167677265676174653a2063616c6c206661696c6564604082015260600190565b600060408201848352602060408185015281855180845260608601915060608382028701019350828701855b8281101561091457605f198887030184526109028683516107cc565b955092840192908401906001016108e6565b509398975050505050505050565b6000848252836020830152606060408301526109416060830184610760565b95945050505050565b604051601f8201601f1916810167ffffffffffffffff81118282101715610973576109736109f3565b604052919050565b60008282101561098d5761098d6109dd565b500390565b60005b838110156109ad578181015183820152602001610995565b838111156109bc576000848401525b50505050565b60006000198214156109d6576109d66109dd565b5060010190565b634e487b7160e01b600052601160045260246000fd5b634e487b7160e01b600052604160045260246000fdfea2646970667358221220c1152f751f29ece4d7bce5287ceafc8a153de9c2c633e3f21943a87d845bd83064736f6c63430008010033"

multicall_deploy_block = contract_creation_block(multicall2.address)


def multicall_same_func_no_input(
    addresses: list,
    method: str, 
    block = None,
    apply_func = None
    ):

    addresses = _clean_addresses(addresses)
    calls = [Call(address, [method], [[address,apply_func]]) for address in addresses]
    return [result for result in Multicall(calls, block_id=block, _w3=web3)().values()]


def multicall_same_func_different_contracts_same_input(
    addresses: list, 
    method: str, 
    input = None, 
    block: Union[int, BlockNumber, None] = None,
    apply_func = None
    ):

    assert input
    addresses = _clean_addresses(addresses)
    calls = [Call(address, [method, input], [[address,apply_func]]) for address in addresses]
    return [result for result in Multicall(calls, block_id=block, _w3=web3)().values()]


def multicall_same_func_same_contract_different_inputs(
    address: Union[str, Address, brownie.Contract, Contract], 
    method: str, 
    inputs: Union[List, Tuple],  
    block: Union[int, BlockNumber, None] = None,
    apply_func = None,
    return_None_on_failure: bool = False
    ):

    assert inputs
    address = _clean_address(address)
    calls = [Call(address, [method, input], [[input,apply_func]]) for input in inputs]
    return [result for result in Multicall(calls, block_id=block, _w3=web3, require_success = not return_None_on_failure)().values()]


def multicall_decimals(
    addresses: List[str], 
    block: Union[int, BlockNumber, None] = None,
    return_None_on_failure: bool = True
    ):

    try: return multicall_same_func_no_input(addresses, 'decimals()(uint256)', block=block)
    except ValueError as e:
        if 'execution reverted' in str(e): pass 
        else: raise
    except (CannotHandleRequest,InsufficientDataBytes): pass
    
    return [_decimals(address,block=block,return_None_on_failure=return_None_on_failure) for address in addresses]

def multicall_totalSupply(
    addresses: List[str], 
    block: Union[int, BlockNumber, None] = None,
    return_None_on_failure: bool = True
    ):

    try: return multicall_same_func_no_input(addresses, 'totalSupply()(uint256)', block=block)
    except (CannotHandleRequest,InsufficientDataBytes): pass
        
    return [_totalSupply(address,block=block,return_None_on_failure=return_None_on_failure) for address in addresses] 


def multicall_balanceOf(
    token_addresses: List[str], 
    hodler_address: str, 
    block: Union[int, BlockNumber, None] = None,
    return_None_on_failure: bool = True # TODO: implement this kwarg
    ):
    return multicall_same_func_different_contracts_same_input(token_addresses, 'balanceOf(address)(uint)', input=hodler_address, block=block)


def fetch_multicall(*calls, block=None):
    # https://github.com/makerdao/multicall
    multicall_input = []
    fn_list = []
    decoded = []

    for contract, fn_name, *fn_inputs in calls:
        fn = getattr(contract, fn_name)

        # check that there aren't multiple functions with the same name
        if hasattr(fn, "_get_fn_from_args"):
            fn = fn._get_fn_from_args(fn_inputs)

        fn_list.append(fn)
        multicall_input.append((contract, fn.encode_input(*fn_inputs)))

    if isinstance(block, int) and block < multicall_deploy_block:
        # use state override to resurrect the contract prior to deployment
        data = multicall2.tryAggregate.encode_input(False, multicall_input)
        call = web3.eth.call(
            {'to': str(multicall2), 'data': data},
            block or 'latest',
            {str(multicall2): {'code': f'0x{multicall2.bytecode}'}},
        )
        result = multicall2.tryAggregate.decode_output(call)
    else:
        result = multicall2.tryAggregate.call(
            False, multicall_input, block_identifier=block or 'latest'
        )

    for fn, (ok, data) in zip(fn_list, result):
        try:
            assert ok, "call failed"
            decoded.append(fn.decode_output(data))
        except (AssertionError, InsufficientDataBytes):
            decoded.append(None)

    return decoded


def multicall_matrix(contracts, params, block="latest"):
    matrix = list(product(contracts, params))
    calls = [[contract, param] for contract, param in matrix]

    results = fetch_multicall(*calls, block=block)

    output = defaultdict(dict)
    for (contract, param), value in zip(matrix, results):
        output[contract][param] = value

    return dict(output)


def batch_call(calls):
    """
    Similar interface but block height as last param. Uses JSON-RPC batch.
    [[contract, 'func', arg, block_identifier]]
    """
    jsonrpc_batch = []
    fn_list = []
    ids = count()

    for contract, fn_name, *fn_inputs, block in calls:
        fn = getattr(contract, fn_name)
        if hasattr(fn, "_get_fn_from_args"):
            fn = fn._get_fn_from_args(fn_inputs)
        fn_list.append(fn)

        jsonrpc_batch.append(
            {
                'jsonrpc': '2.0',
                'id': next(ids),
                'method': 'eth_call',
                'params': [
                    {'to': str(contract), 'data': fn.encode_input(*fn_inputs)},
                    block,
                ],
            }
        )

    response = requests.post(web3.provider.endpoint_uri, json=jsonrpc_batch).json()
    return [
        fn.decode_output(res['result'])
        for res in sorted(response, key=itemgetter('id'))
    ]


def _clean_addresses(
    addresses: Sequence[Any]
):

    return [_clean_address(address) for address in addresses]


def _clean_address(
    address: Any
    ):

    if type(address) not in SUPPORTED_INPUT_TYPES:
        raise TypeError(f'Unsupported input type: {type(address)}')
    
    if type(address) != str: 
        address = str(address)

    return convert.to_address(address)
