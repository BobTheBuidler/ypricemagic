from tests.fixtures import mainnet_only
from y.prices import magic


@mainnet_only
def test_stargate_lp_price():
    token = "0xdf0770dF86a8034b3EFEf0A1Bb3c889B8332FF56"  # S*USDC
    price = magic.get_price(token, 17_000_000, skip_cache=True)
    assert price and price > 0
