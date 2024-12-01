from tests.fixtures import mainnet_only
from y.prices import magic


@mainnet_only
def test_piedao_get_price():
    """Test the `get_price` function from the `magic` module for a specific token.

    This test checks the price of a specific token at a given block number
    using the `get_price` function from the `magic` module. It ensures that
    the price returned matches the expected value.

    Examples:
        >>> test_piedao_get_price()
        # This will assert the price of the token at block 15,000,000.

    See Also:
        - :func:`y.prices.magic.get_price`
    """
    token = "0x9A48BD0EC040ea4f1D3147C025cd4076A2e71e3e"
    assert magic.get_price(token, 15_000_000, skip_cache=True) == 1.0000156215170668
