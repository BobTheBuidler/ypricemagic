from tests.fixtures import mainnet_only
from y.prices import magic

@mainnet_only
def test_curve():
    token = "0xAA5A67c256e27A5d80712c51971408db3370927D" # DOLA3POOL3CRV-f
    assert magic.get_price(token, 15_000_000) == 1.0029303734731028

    token = "0x29059568bB40344487d62f7450E78b8E6C74e0e5" # YFIETH-f
    assert magic.get_price(token, 15_000_000) == 4713.219279160143
