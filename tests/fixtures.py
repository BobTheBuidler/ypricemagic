from typing import Iterable, List, Tuple

import numpy as np
import pytest
from brownie import Contract as BrownieContract
from brownie import chain
from brownie.convert.datatypes import EthAddress
from y import convert
from y.classes.common import ERC20
from y.contracts import Contract, contract_creation_block
from y.networks import Network
from y.typing import Address, Block

mainnet_only = pytest.mark.skipif(
    chain.id != Network.Mainnet, reason="This test is only applicable on mainnet"
)

def blocks_for_contract(address: Address, count: int = 5) -> List[Block]:
    address = convert.to_address(address)
    return [int(block) for block in np.linspace(contract_creation_block(address) + 10000, chain.height, count)]

def mutate_address(address: Address) -> Tuple[str,str,str,EthAddress]:
    """
    Returns the same address in various forms for testing.
    """
    return (
        address.lower(),
        address[:2] + address[2:].upper(),
        convert.to_address(address),
        EthAddress(address)
    )

def mutate_addresses(addresses: Iterable[Address]):
    return [mutation for address in addresses for mutation in mutate_address(address)]

def mutate_contract(contract_address: Address) -> Tuple[str,str,str,EthAddress,BrownieContract]:
    """
    Returns the same contract address in various forms for testing.
    """
    mutations = list(mutate_address(contract_address))
    mutations.append(Contract(contract_address))
    return tuple(mutations)

def mutate_contracts(addresses: Iterable[Address]):
    return [mutation for address in addresses for mutation in mutate_contract(address)]

def mutate_token(token: Address) -> Tuple[str,str,str,EthAddress,BrownieContract,int,ERC20]:
    """
    Returns the same token address in various forms for testing.
    """
    mutations = list(mutate_contract(token))
    mutations.append(ERC20(token))
    mutations.append(int(token,16))
    return tuple(mutations)

def mutate_tokens(addresses: Iterable[Address]):
    return [mutation for address in addresses for mutation in mutate_token(address)]
