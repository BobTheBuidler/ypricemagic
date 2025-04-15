import pytest
from y.constants import STABLECOINS
from y.prices import magic

from tests.fixtures import blocks_for_contract

STABLECOINS = STABLECOINS.keys()


# TODO Implement this after implementing non-stable stables to validate tokens' spots in `STABLECOINS`.
@pytest.mark.parametrize("token", STABLECOINS)
def test_stablecoins(token):
    """Placeholder test for stablecoin prices.

    This test iterates over a series of blocks for each stablecoin token provided in
    :data:`y.constants.STABLECOINS` and asserts that the price is exactly equal to 1.
    This strict equality is required for the current implementation of stable tokens.
    In a future revision, when non-stable stables are implemented, tolerances for
    rounding and scaling issues may be introduced.

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