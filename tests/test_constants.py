import pytest
from eth_utils import is_checksum_address

from tests.fixtures import blocks_for_contract
from y.constants import ROUTING_TOKENS, STABLECOINS, usdc, weth
from y.networks import Network
from y.prices import magic


@pytest.mark.parametrize("token", STABLECOINS)
def test_stablecoins(token):
    """Placeholder test for stablecoin prices.

    This test iterates over a series of blocks for each stablecoin token provided in
    :data:`y.constants.STABLECOINS` and asserts that the price is exactly equal to 1.
    This strict equality is enforced for the current implementation of stable tokens.
    In a future revision when non‐stable stables are implemented, tolerances for
    rounding and scaling issues may be introduced.

    Args:
        token: The stablecoin token address to be tested.

    See Also:
        :func:`y.get_price`: for retrieving token prices.
        :func:`tests.fixtures.blocks_for_contract`: for generating block numbers for testing.
    """
    for block in blocks_for_contract(token, 20):
        # NOTE Placeholder.
        assert magic.get_price(token, block, skip_cache=True) == 1, "Stablecoin price not $1"


def test_routing_tokens_shape():
    expected = {
        Network.Mainnet: 4,
        Network.Arbitrum: 3,
        Network.Optimism: 3,
        Network.Base: 3,
    }

    assert set(expected).issubset(ROUTING_TOKENS)
    assert ROUTING_TOKENS[Network.Mainnet][:2] == [weth.address, usdc.address]

    for chain_id, expected_len in expected.items():
        tokens = ROUTING_TOKENS[chain_id]
        assert len(tokens) == expected_len
        assert all(is_checksum_address(address) for address in tokens)
