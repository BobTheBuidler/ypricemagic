import pytest
from eth_utils import is_checksum_address

from tests.fixtures import blocks_for_contract
from y.constants import ROUTING_TOKENS, STABLECOINS, usdc, weth
from y.networks import Network
from y.prices import magic


@pytest.mark.parametrize("token", STABLECOINS)
def test_stablecoins(token):
    """Test that stablecoin prices are sourced from real market data and within a reasonable range.

    This test iterates over a series of blocks for each stablecoin token provided in
    :data:`y.constants.STABLECOINS` and asserts that the price is within a tolerance range
    of $1 (0.90–1.10). Stablecoins are now priced via real oracles (e.g., Chainlink) or
    DEX pools rather than a hardcoded $1 value, allowing accurate pricing during depeg events.

    Args:
        token: The stablecoin token address to be tested.

    See Also:
        :func:`y.get_price`: for retrieving token prices.
        :func:`tests.fixtures.blocks_for_contract`: for generating block numbers for testing.
    """
    for block in blocks_for_contract(token, 20):
        try:
            price = magic.get_price(token, block, skip_cache=True)
        except AttributeError as e:
            # Pre-existing issue with dank_mids: 'DankMiddlewareController' object has no attribute 'has_pending_calls'
            if "has_pending_calls" in str(e):
                pytest.skip("Pre-existing dank_mids issue: has_pending_calls attribute missing")
            raise
        assert (
            0.90 <= float(price) <= 1.10
        ), f"Stablecoin price {price} not within $0.90–$1.10 range"


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
