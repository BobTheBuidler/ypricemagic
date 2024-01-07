
import pytest
from y.constants import STABLECOINS
from y.prices import magic

from tests.fixtures import blocks_for_contract

STABLECOINS = STABLECOINS.keys()

# TODO Implement this after imlementing non-stable stables to validate tokens' spots in `STABLECOINS`.
@pytest.mark.parametrize('token',STABLECOINS)
def test_stablecoins(token):
    for block in blocks_for_contract(token,20):
        # NOTE Placeholder.
        assert magic.get_price(token, block, skip_cache=True) == 1, 'Stablecoin price not $1'
