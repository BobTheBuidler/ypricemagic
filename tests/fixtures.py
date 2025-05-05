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

    This function generates a list of block numbers that are evenly spaced between the block
    obtained from :func:`~y.contracts.contract_creation_block` plus an offset of 10,000 and the current
    block height.

    Args:
        address: The address of the contract.
        count: Number of blocks to generate; default is 5.

    Returns:
        A list of block numbers where the first number is computed as
        contract_creation_block(address) + 10,000 and the remaining numbers are evenly spaced up to the current block height.

    Examples:
        Suppose that :func:`~y.contracts.contract_creation_block` returns 1000 and the current block height is 20000.
        Then the first block is 1000 + 10000 = 11000.
        With count=3, one possible output is:

        >>> blocks = blocks_for_contract("0x123", count=3)
        >>> blocks
        [11000, 15500, 20000]
        >>> isinstance(blocks, list)
        True

    See Also:
        :func:`~y.contracts.contract_creation_block`
    """
    address = convert.to_address(address)
    return [
        int(block)
        for block in np.linspace(contract_creation_block(address) + 10000, chain.height, count)
    ]


def mutate_address(address: Address) -> Tuple[str, str, str, EthAddress]:
    """
    Returns the same address in various forms for testing.

    This function returns a tuple with various representations of the given address:
    1. Lowercase string.
    2. Checksum address string.
    3. Address object produced via :func:`~y.convert.to_address`.
    4. EthAddress object.

    Args:
        address: The original address.

    Returns:
        A tuple containing:
            - Lowercase string.
            - Checksum address string.
            - Address object.
            - EthAddress object.

    Examples:
        >>> result = mutate_address("0xAbCdEf1234567890")
        >>> result[0]
        '0xabcdef1234567890'
        >>> isinstance(result[2], str)
        True

    See Also:
        :func:`~y.convert.to_address`
    """
    return (
        address.lower(),
        address[:2] + address[2:].upper(),
        convert.to_address(address),
        EthAddress(address),
    )


def mutate_addresses(addresses: Iterable[Address]):
    """
    Return a list of all mutated address representations for each address in the given iterable.

    Examples:
        >>> results = mutate_addresses(["0xAbCdEf1234567890", "0x1234567890abcdef"])
        >>> len(results)
        8

    See Also:
        :func:`mutate_address`
    """
    return list(concat(map(mutate_address, addresses)))


def mutate_contract(
    contract_address: Address,
) -> Tuple[str, str, str, EthAddress, BrownieContract]:
    """
    Returns the same contract address in various forms for testing.

    This function returns a tuple including various mutated representations:
    1-4. The different address forms returned by :func:`mutate_address`.
    5. A Brownie Contract object created with :class:`~brownie.Contract`.

    Args:
        contract_address: The original contract address.

    Returns:
        A tuple containing:
            - Lowercase string.
            - Checksum address string.
            - Address object.
            - EthAddress object.
            - Brownie Contract object.

    Examples:
        >>> result = mutate_contract("0xAbCdEf1234567890")
        >>> isinstance(result[4], BrownieContract)
        True

    See Also:
        :func:`mutate_address`
    """
    mutations = list(mutate_address(contract_address))
    mutations.append(Contract(contract_address))
    return tuple(mutations)


def mutate_contracts(addresses: Iterable[Address]):
    """
    Return a list of all mutated contract representations for each address in the given iterable.

    Each address is mutated into five representations (see :func:`mutate_contract`),
    so if two addresses are provided, the output will contain 10 items.

    Examples:
        >>> results = mutate_contracts(["0xAbCdEf1234567890", "0x1234567890abcdef"])
        >>> results  # Should contain 10 items
        [<mutated item>, <mutated item>, ..., <mutated item>]
        >>> len(results) == 10
        True

    See Also:
        :func:`mutate_contract`
    """
    return list(concat(map(mutate_contract, addresses)))


def mutate_token(
    token: Address,
) -> Tuple[str, str, str, EthAddress, BrownieContract, ERC20, int]:
    """
    Returns the same token address in various forms for testing.

    This function returns a tuple with different representations of the token address in the following order:
    1. Lowercase string.
    2. Checksum address string.
    3. Address object produced via :func:`~y.convert.to_address`.
    4. EthAddress object.
    5. Brownie Contract object created with :class:`~y.contracts.Contract`.
    6. An ERC20 object created with :class:`~y.classes.common.ERC20`.
    7. The integer conversion of the token address in hexadecimal format.

    Args:
        token: The original token address.

    Returns:
        A tuple containing:
            - Lowercase string representation.
            - Checksum string representation.
            - Address object.
            - EthAddress object.
            - Brownie Contract object.
            - ERC20 object.
            - Integer representation of the token address.

    Examples:
        >>> result = mutate_token("0xAbCdEf1234567890")
        >>> isinstance(result[5], ERC20)
        True
        >>> isinstance(result[6], int)
        True

    See Also:
        :func:`mutate_contract`
        :class:`~y.classes.common.ERC20`
    """
    mutations = list(mutate_contract(token))
    mutations.append(ERC20(token))
    mutations.append(int(token, 16))
    return tuple(mutations)


def mutate_tokens(addresses: Iterable[Address]):
    """
    Return a list of all mutated token representations for each address in the given iterable.

    Each address is mutated into seven representations (see :func:`mutate_token`),
    so if two addresses are provided, the output will contain 14 items.

    Examples:
        >>> results = mutate_tokens(["0xAbCdEf1234567890", "0x1234567890abcdef"])
        >>> len(results) == 14
        True

    See Also:
        :func:`mutate_token`
    """
    return list(concat(map(mutate_token, addresses)))


@pytest.fixture
def async_uni_v1():
    """
    A pytest fixture that yields an instance of :class:`~y.prices.dex.uniswap.v1.UniswapV1` in asynchronous mode.

    Examples:
        >>> async def test_example(async_uni_v1):
        ...     uniswap = async_uni_v1
        ...     # Use uniswap in asynchronous tests
        ...     assert uniswap.asynchronous is True

    See Also:
        :class:`~y.prices.dex.uniswap.v1.UniswapV1`
    """
    yield UniswapV1(asynchronous=True)
