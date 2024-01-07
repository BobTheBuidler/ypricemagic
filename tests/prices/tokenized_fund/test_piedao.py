
from tests.fixtures import mainnet_only
from y.prices import magic

@mainnet_only
def test_piedao_get_price():
    token = "0x9A48BD0EC040ea4f1D3147C025cd4076A2e71e3e"
    assert magic.get_price(token, 15_000_000, skip_cache=True) == 1.0000156215170668