import dank_mids
import pytest
from brownie import ZERO_ADDRESS, chain
from multicall import Call

from tests.fixtures import blocks_for_contract
from tests.test_constants import STABLECOINS
from y.classes.common import ERC20
from y.constants import WRAPPED_GAS_COIN, wbtc
from y.contracts import Contract
from y.exceptions import NoProxyImplementation, call_reverted
from y.networks import Network

TOKENS = list(STABLECOINS) + [WRAPPED_GAS_COIN, wbtc.address]

if chain.id == Network.Mainnet:
    # MKR symbol and name methods return bytes, we want to test that our code returns strings
    MKR = "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2"
    TOKENS.append(MKR)

OLD_SUSD = "0x57Ab1E02fEE23774580C119740129eAC7081e9D3"

TOKENS_BY_BLOCK = [(token, block) for token in TOKENS for block in blocks_for_contract(token)]


@pytest.mark.parametrize("token", TOKENS)
def test_erc20_sync(token):
    """
    Test the synchronous functionality of the :class:`~y.classes.common.ERC20` class.

    This test checks various properties and methods of the :class:`~y.classes.common.ERC20` class for a given token,
    including interactions with the :class:`~y.contracts.Contract` class to fetch the contract for the token.

    Args:
        token: The address of the token to test.

    Raises:
        AssertionError: If any of the assertions fail.

    Note:
        This test will be skipped for the old sUSD token with the address
        `0x57Ab1E02fEE23774580C119740129eAC7081e9D3`.

    See Also:
        - :class:`~y.classes.common.ERC20`
        - :class:`~y.contracts.Contract`
    """
    token = ERC20(token)

    if token.address == OLD_SUSD:
        pytest.skip("Not applicable to deprecated sUSD.")

    block = chain.height
    assert isinstance(token.contract, Contract), f"Cannot fetch contract for token {token}"
    assert isinstance(token.build_name, str), f"Cannot fetch build name for token {token}"
    assert isinstance(token.symbol, str), f"Cannot fetch symbol for token {token}"
    assert isinstance(token.name, str), f"Cannot fetch name for token {token}"
    assert 10**token.decimals == token.scale, f"Incorrect scale fetched for token {token}"
    assert token.total_supply(block) / token.scale == token.total_supply_readable(
        block
    ), f"Incorrect total supply readable for token {token}"
    assert token.price(), f"Cannot fetch price for token {token}"


@pytest.mark.parametrize("token", TOKENS)
@pytest.mark.asyncio_cooperative
async def test_erc20_async(token):
    """
    Test the asynchronous functionality of the :class:`~y.classes.common.ERC20` class.

    This test checks various properties and methods of the :class:`~y.classes.common.ERC20` class for a given token asynchronously,
    including interactions with the :class:`~y.contracts.Contract` class to fetch the contract for the token.

    Args:
        token: The address of the token to test.

    Raises:
        AssertionError: If any of the assertions fail.

    Note:
        This test will be skipped for the old sUSD token with the address
        `0x57Ab1E02fEE23774580C119740129eAC7081e9D3`.

    See Also:
        - :class:`~y.classes.common.ERC20`
        - :class:`~y.contracts.Contract`
        - :mod:`dank_mids` for asynchronous operations
    """
    token = ERC20(token, asynchronous=True)

    if token.address == OLD_SUSD:
        pytest.skip("Not applicable to deprecated sUSD.")

    block = await dank_mids.eth.block_number
    assert isinstance(token.contract, Contract), f"Cannot fetch contract for token {token}"
    assert isinstance(await token.build_name, str), f"Cannot fetch build name for token {token}"
    assert isinstance(await token.symbol, str), f"Cannot fetch symbol for token {token}"
    assert isinstance(await token.name, str), f"Cannot fetch name for token {token}"
    assert (
        10 ** await token.decimals == await token.scale
    ), f"Incorrect scale fetched for token {token}"
    assert await token.total_supply(block) / await token.scale == await token.total_supply_readable(
        block
    ), f"Incorrect total supply readable for token {token}"
    assert await token.price(), f"Cannot fetch price for token {token}"


@pytest.mark.parametrize("token,block", TOKENS_BY_BLOCK)
@pytest.mark.asyncio_cooperative
async def test_erc20_at_block(token, block):
    """
    Test the :class:`~y.classes.common.ERC20` class at specific blocks.

    This test checks the total supply and price of the :class:`~y.classes.common.ERC20` token at specific blocks asynchronously,
    including interactions with the :class:`~y.contracts.Contract` class to fetch the contract for the token.

    Args:
        token: The address of the token to test.
        block: The block number to test at.

    Raises:
        AssertionError: If any of the assertions fail.
        NoProxyImplementation: If the token is a problematic proxy.

    Note:
        This test will be skipped for the old sUSD token with the address
        `0x57Ab1E02fEE23774580C119740129eAC7081e9D3` after its migration block.
        It will also be skipped for proxy contracts with implementation not set.

    See Also:
        - :class:`~y.classes.common.ERC20`
        - :class:`~y.contracts.Contract`
        - :mod:`dank_mids` for asynchronous operations
    """
    token = ERC20(token, asynchronous=True)

    if token.address == OLD_SUSD and block >= 13222927:
        pytest.skip("Not applicable to the old sUSD after migration block.")

    # NOTE Some proxy tokens would fail tests in early days because no implementation is specified.
    try:
        if await Call(token.address, "implementation()(address)", block_id=block) == ZERO_ADDRESS:
            pytest.skip(f"Not applicable to proxy contracts with implementation not set.")
    except Exception as e:
        if not call_reverted(e):
            raise

    # NOTE We've validated token is not problematic proxy, proceed with test.
    try:
        # NOTE also tests ERC20._decimals
        assert await token.total_supply(block) / await token._scale(
            block
        ) == await token.total_supply_readable(
            block
        ), f"Incorrect total supply readable for token {token}"
    except NoProxyImplementation:
        pass

    assert await token.price(block), f"Cannot fetch price for token {token}"
