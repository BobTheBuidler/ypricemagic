
import pytest
from y.constants import STABLECOINS
from y.prices import magic

from tests.fixtures import blocks_for_contract, mutate_token

STABLECOINS = [
    mutation
    for address in STABLECOINS.keys()
    for mutation in mutate_token(address)
]

# TODO Implement this after imlementing non-stable stables to validate tokens' spots in `STABLECOINS`.
@pytest.mark.parametrize('token',STABLECOINS)
def test_stablecoins(token):
    for block in blocks_for_contract(token,20):
        # NOTE Placeholder.
        assert magic.get_price(token) == 1, 'Stablecoin price not $1'
