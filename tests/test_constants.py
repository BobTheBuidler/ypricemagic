import pytest
from eth_utils import is_checksum_address

from tests.fixtures import blocks_for_contract
from y.constants import ROUTING_TOKENS, STABLECOINS, usdc, weth
from y.networks import Network
from y.prices import magic


@pytest.mark.parametrize("token", STABLECOINS)
def test_stablecoins(token):
    """Test stablecoin pricing: USDC is exactly $1, others are near $1 from real price sources.

    USDC is hardcoded to $1 via the 'stable usd' bucket. All other stablecoins (USDT, DAI, etc.)
    go through real price resolution (Chainlink, DEX, etc.) and should return prices
    between $0.95 and $1.05 under normal market conditions.

    Args:
        token: The stablecoin token address to be tested.

    See Also:
        :func:`y.get_price`: for retrieving token prices.
        :func:`tests.fixtures.blocks_for_contract`: for generating block numbers for testing.
    """
    for block in blocks_for_contract(token, 20):
        price = magic.get_price(token, block, skip_cache=True)
        if usdc is not None and token == usdc.address:
            assert price == 1.0, f"USDC price should be exactly $1, got {price}"
        else:
            assert (
                0.95 <= float(price) <= 1.05
            ), f"Stablecoin {token} price {price} not in expected range [0.95, 1.05]"


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
