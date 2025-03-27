from typing import Iterable, List, Tuple

import numpy as np
import pytest
from brownie import Contract as BrownieContract
from brownie import chain
from brownie.convert.datatypes import EthAddress
from eth_utils.toolz import concat
from y import convert
from y.classes.common import ERC20
from y.contracts import Contract, contract_creation_block
from y.datatypes import Address, Block
from y.prices.dex.uniswap.v1 import UniswapV1

from y.networks import Network

mainnet_only = pytest.mark.skipif(
    chain.id != Network.Mainnet, reason="This test is only applicable on mainnet"
)
"""
A pytest marker to skip tests that are only applicable on the Ethereum mainnet.
"""

optimism_only = pytest.mark.skipif(
    chain.id != Network.Optimism, reason="This test is only applicable on optimism"
)
"""
A pytest marker to skip tests that are only applicable on the Optimism network.
"""

async_test = pytest.mark.asyncio_cooperative
"""
A pytest marker for concurrent asynchronous tests using asyncio_cooperative.
"""


def blocks_for_contract(address: Address, count: int = 5) -> List[Block]:
    """
    Generate a list of block numbers for testing a contract.

    Args:
        address: The address of the contract.
        count: The number of blocks to generate (default is 5).

    Returns:
        A list of block numbers evenly spaced between the contract's creation and the current block height.
    """
    address = convert.to_address(address)
    return [
        int(block)
        for block in np.linspace(
            contract_creation_block(address) + 10000, chain.height, count
        )
    ]


def mutate_address(address: Address) -> Tuple[str, str, str, EthAddress]:
    """
    Returns the same address in various forms for testing.

    Args:
        address: The original address.

    Returns:
        A tuple containing the address in four different forms:
        1. Lowercase string
        2. Checksum address string
        3. Address object
        4. EthAddress object
    """
    return (
        address.lower(),
        address[:2] + address[2:].upper(),
        convert.to_address(address),
        EthAddress(address),
    )


def mutate_addresses(addresses: Iterable[Address]):
    return list(concat(map(mutate_address, addresses)))


def mutate_contract(
    contract_address: Address,
) -> Tuple[str, str, str, EthAddress, BrownieContract]:
    """
    Returns the same contract address in various forms for testing.
    """
    mutations = list(mutate_address(contract_address))
    mutations.append(Contract(contract_address))
    return tuple(mutations)


def mutate_contracts(addresses: Iterable[Address]):
    return list(concat(map(mutate_contract, addresses)))


def mutate_token(
    token: Address,
) -> Tuple[str, str, str, EthAddress, BrownieContract, int, ERC20]:
    """
    Returns the same token address in various forms for testing.
    """
    mutations = list(mutate_contract(token))
    mutations.append(ERC20(token))
    mutations.append(int(token, 16))
    return tuple(mutations)


def mutate_tokens(addresses: Iterable[Address]):
    return list(concat(map(mutate_token, addresses)))


@pytest.fixture
def async_uni_v1():
    yield UniswapV1(asynchronous=True)
