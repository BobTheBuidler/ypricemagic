import asyncio
import logging
from typing import Any, Callable, Iterable, List, Optional, Tuple, Union

import a_sync
import brownie
import contextlib
from brownie import chain
from eth_abi.exceptions import InsufficientDataBytes
from multicall import Call
from web3.exceptions import CannotHandleRequest

from y import convert
from y.contracts import Contract, contract_creation_block
from y.datatypes import Address, AddressOrContract, AnyAddressType, Block
from y.exceptions import continue_if_call_reverted
from y.interfaces.multicall2 import MULTICALL2_ABI
from y.networks import Network
from y.utils.dank_mids import dank_w3
from y.utils.raw_calls import _decimals, _totalSupply

logger = logging.getLogger(__name__)

MULTICALL2 = {
    Network.Mainnet:            "0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696",
    Network.Arbitrum:           "0x842eC2c7D803033Edf55E478F461FC547Bc54EB2",
    Network.Avalanche:          "0xdf2122931FEb939FB8Cf4e67Ea752D1125e18858",
    Network.BinanceSmartChain:  "0xfF6FD90A470Aaa0c1B8A54681746b07AcdFedc9B",
    Network.Fantom:             "0xBAD2B082e2212DE4B065F636CA4e5e0717623d18",
    Network.Harmony:            "0x34b415f4d3b332515e66f70595ace1dcf36254c5",
    Network.Heco:               "0xd1F3BE686D64e1EA33fcF64980b65847aA43D79C",
    Network.Moonriver:          "0xaeF00A0Cf402D9DEdd54092D9cA179Be6F9E5cE3",
    Network.Polygon:            "0xc8E51042792d7405184DfCa245F2d27B94D013b6",
    Network.xDai:               "0x9903f30c1469d8A2f415D4E8184C93BD26992573",
    Network.Aurora:             "0xe0e3887b158F7F9c80c835a61ED809389BC08d1b",
    Network.Cronos:             "0x5e954f5972EC6BFc7dECd75779F10d848230345F",
    Network.Optimism:           "0xcA11bde05977b3631167028862bE2a173976CA11", # Multicall 3
    Network.Base:               "0xcA11bde05977b3631167028862bE2a173976CA11", # mc3
}.get(chain.id)

multicall = None
multicall2 = brownie.Contract.from_abi("Multicall2",MULTICALL2, MULTICALL2_ABI) if chain.id in [Network.Harmony,Network.Cronos] else Contract(MULTICALL2)

# the address doesn't matter, it just needs to have code
code = "0x608060405234801561001057600080fd5b50600436106100b45760003560e01c806372425d9d1161007157806372425d9d1461013d57806386d516e814610145578063a8b0574e1461014d578063bce38bd714610162578063c3077fa914610182578063ee82ac5e14610195576100b4565b80630f28c97d146100b9578063252dba42146100d757806327e86d6e146100f8578063399542e91461010057806342cbb15c146101225780634d2301cc1461012a575b600080fd5b6100c16101a8565b6040516100ce919061083b565b60405180910390f35b6100ea6100e53660046106bb565b6101ac565b6040516100ce9291906108ba565b6100c1610340565b61011361010e3660046106f6565b610353565b6040516100ce93929190610922565b6100c161036b565b6100c161013836600461069a565b61036f565b6100c161037c565b6100c1610380565b610155610384565b6040516100ce9190610814565b6101756101703660046106f6565b610388565b6040516100ce9190610828565b6101136101903660046106bb565b610533565b6100c16101a3366004610748565b610550565b4290565b8051439060609067ffffffffffffffff8111156101d957634e487b7160e01b600052604160045260246000fd5b60405190808252806020026020018201604052801561020c57816020015b60608152602001906001900390816101f75790505b50905060005b835181101561033a5760008085838151811061023e57634e487b7160e01b600052603260045260246000fd5b6020026020010151600001516001600160a01b031686848151811061027357634e487b7160e01b600052603260045260246000fd5b60200260200101516020015160405161028c91906107f8565b6000604051808303816000865af19150503d80600081146102c9576040519150601f19603f3d011682016040523d82523d6000602084013e6102ce565b606091505b5091509150816102f95760405162461bcd60e51b81526004016102f090610885565b60405180910390fd5b8084848151811061031a57634e487b7160e01b600052603260045260246000fd5b602002602001018190525050508080610332906109c2565b915050610212565b50915091565b600061034d60014361097b565b40905090565b43804060606103628585610388565b90509250925092565b4390565b6001600160a01b03163190565b4490565b4590565b4190565b6060815167ffffffffffffffff8111156103b257634e487b7160e01b600052604160045260246000fd5b6040519080825280602002602001820160405280156103eb57816020015b6103d8610554565b8152602001906001900390816103d05790505b50905060005b825181101561052c5760008084838151811061041d57634e487b7160e01b600052603260045260246000fd5b6020026020010151600001516001600160a01b031685848151811061045257634e487b7160e01b600052603260045260246000fd5b60200260200101516020015160405161046b91906107f8565b6000604051808303816000865af19150503d80600081146104a8576040519150601f19603f3d011682016040523d82523d6000602084013e6104ad565b606091505b509150915085156104d557816104d55760405162461bcd60e51b81526004016102f090610844565b604051806040016040528083151581526020018281525084848151811061050c57634e487b7160e01b600052603260045260246000fd5b602002602001018190525050508080610524906109c2565b9150506103f1565b5092915050565b6000806060610543600185610353565b9196909550909350915050565b4090565b60408051808201909152600081526060602082015290565b80356001600160a01b038116811461058357600080fd5b919050565b600082601f830112610598578081fd5b8135602067ffffffffffffffff808311156105b5576105b56109f3565b6105c2828385020161094a565b83815282810190868401865b8681101561068c57813589016040601f198181848f030112156105ef578a8bfd5b6105f88261094a565b6106038a850161056c565b81528284013589811115610615578c8dfd5b8085019450508d603f850112610629578b8cfd5b898401358981111561063d5761063d6109f3565b61064d8b84601f8401160161094a565b92508083528e84828701011115610662578c8dfd5b808486018c85013782018a018c9052808a01919091528652505092850192908501906001016105ce565b509098975050505050505050565b6000602082840312156106ab578081fd5b6106b48261056c565b9392505050565b6000602082840312156106cc578081fd5b813567ffffffffffffffff8111156106e2578182fd5b6106ee84828501610588565b949350505050565b60008060408385031215610708578081fd5b82358015158114610717578182fd5b9150602083013567ffffffffffffffff811115610732578182fd5b61073e85828601610588565b9150509250929050565b600060208284031215610759578081fd5b5035919050565b60008282518085526020808601955080818302840101818601855b848110156107bf57858303601f19018952815180511515845284015160408585018190526107ab818601836107cc565b9a86019a945050509083019060010161077b565b5090979650505050505050565b600081518084526107e4816020860160208601610992565b601f01601f19169290920160200192915050565b6000825161080a818460208701610992565b9190910192915050565b6001600160a01b0391909116815260200190565b6000602082526106b46020830184610760565b90815260200190565b60208082526021908201527f4d756c746963616c6c32206167677265676174653a2063616c6c206661696c656040820152601960fa1b606082015260800190565b6020808252818101527f4d756c746963616c6c206167677265676174653a2063616c6c206661696c6564604082015260600190565b600060408201848352602060408185015281855180845260608601915060608382028701019350828701855b8281101561091457605f198887030184526109028683516107cc565b955092840192908401906001016108e6565b509398975050505050505050565b6000848252836020830152606060408301526109416060830184610760565b95945050505050565b604051601f8201601f1916810167ffffffffffffffff81118282101715610973576109736109f3565b604052919050565b60008282101561098d5761098d6109dd565b500390565b60005b838110156109ad578181015183820152602001610995565b838111156109bc576000848401525b50505050565b60006000198214156109d6576109d66109dd565b5060010190565b634e487b7160e01b600052601160045260246000fd5b634e487b7160e01b600052604160045260246000fdfea2646970667358221220c1152f751f29ece4d7bce5287ceafc8a153de9c2c633e3f21943a87d845bd83064736f6c63430008010033"

multicall_deploy_block = contract_creation_block(multicall2.address)


@a_sync.a_sync(default='sync')
async def multicall_same_func_no_input(
    addresses: Iterable[AnyAddressType],
    method: str, 
    block: Optional[Block] = None,
    apply_func: Optional[Callable] = None,
    return_None_on_failure: bool = False
    ) -> List[Any]:

    addresses = _clean_addresses(addresses)
    results = await asyncio.gather(*[Call(address, [method], [[address,apply_func]], block_id=block).coroutine() for address in addresses])
    return [v for call in results for k, v in call.items()]


@a_sync.a_sync(default='sync')
async def multicall_same_func_same_contract_different_inputs(
    address: AnyAddressType, 
    method: str, 
    inputs: Union[List, Tuple],  
    block: Optional[Block] = None,
    apply_func: Optional[Callable] = None,
    return_None_on_failure: bool = False
    ) -> List[Any]:
    assert inputs
    address = convert.to_address(address)
    results = await asyncio.gather(
        *[Call(address, [method, input], [[input,apply_func]], block_id=block).coroutine() for input in inputs],
        return_exceptions=return_None_on_failure,
    )
    if return_None_on_failure:
        for i, result in enumerate(results[:]):
            if isinstance(result, Exception):
                continue_if_call_reverted(result)
                results[i] = {i: None}
    return [result for call in results for key, result in call.items()]


@a_sync.a_sync(default='sync')
async def multicall_decimals(
    addresses: Iterable[AddressOrContract], 
    block: Optional[Block] = None,
    return_None_on_failure: bool = True
    ) -> List[int]:

    try: 
        return await asyncio.gather(*[Call(str(address), ['decimals()(uint256)'], block_id=block).coroutine() for address in addresses])
    except (CannotHandleRequest,InsufficientDataBytes):
        pass # TODO investigate these
    except Exception as e:
        continue_if_call_reverted(e)

    return await asyncio.gather(*[_decimals(address,block=block,return_None_on_failure=return_None_on_failure) for address in addresses])

@a_sync.a_sync(default='sync')
async def multicall_totalSupply(
    addresses: Iterable[AddressOrContract], 
    block: Optional[Block] = None,
    return_None_on_failure: bool = True
    ) -> List[int]:

    with contextlib.suppress(CannotHandleRequest, InsufficientDataBytes):
        return await multicall_same_func_no_input(addresses, 'totalSupply()(uint256)', block=block, sync=False)
    return [await _totalSupply(address,block=block,return_None_on_failure=return_None_on_failure, sync=False) for address in addresses] 


#yLazyLogger(logger)
@a_sync.a_sync(default='sync')
async def fetch_multicall(*calls: Any, block: Optional[Block] = None) -> List[Optional[Any]]:
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
        call = dank_w3.eth.call(
            {'to': str(multicall2), 'data': data},
            block or 'latest',
            {str(multicall2): {'code': f'0x{multicall2.bytecode}'}},
        )
        result = multicall2.tryAggregate.decode_output(call)
    else:
        result = await multicall2.tryAggregate.coroutine(
            False, multicall_input, block_identifier=block or 'latest'
        )

    for fn, (ok, data) in zip(fn_list, result):
        try:
            assert ok, "call failed"
            decoded.append(fn.decode_output(data))
        except (AssertionError, InsufficientDataBytes):
            decoded.append(None)

    return decoded


#yLazyLogger(logger)
def _clean_addresses(
    addresses: Iterable[AnyAddressType]
    ) -> List[Address]:

    return [convert.to_address(address) for address in addresses]
