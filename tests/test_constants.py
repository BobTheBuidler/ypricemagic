import pytest
from y.constants import STABLECOINS
from y.prices import magic

from tests.fixtures import blocks_for_contract

STABLECOINS = STABLECOINS.keys()


# TODO Implement this after implementing non-stable stables to validate tokens' spots in `STABLECOINS`.
@pytest.mark.parametrize("token", STABLECOINS)
def test_stablecoins(token):
    """
    Placeholder test for stablecoin prices.

    This test is intended to validate that the price of each stablecoin in the `STABLECOINS` list is $1.
    However, it is currently a placeholder and not fully implemented. The test will iterate over a set
    of blocks for each stablecoin contract and assert that the price is $1.

    Args:
        token: The stablecoin token address to be tested.

    See Also:
        - :func:`y.prices.magic.get_price` for retrieving token prices.
        - :func:`tests.fixtures.blocks_for_contract` for generating block numbers for testing.
    """
    for block in blocks_for_contract(token, 20):
        # NOTE Placeholder.
        assert (
            magic.get_price(token, block, skip_cache=True) == 1
        ), "Stablecoin price not $1"
