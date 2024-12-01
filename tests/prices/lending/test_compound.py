import pytest
from tests.fixtures import blocks_for_contract
from y.prices.lending.compound import CToken, compound

CTOKENS = [
    ctoken.address
    for troller in compound.trollers.values()
    for ctoken in troller.__markets__(sync=True)
]
"""A list of CToken addresses to be tested."""


@pytest.mark.parametrize("token", CTOKENS)
def test_compound_pricing_sync(token):
    """
    Test the synchronous pricing of Compound tokens.

    This test iterates over a list of CToken addresses, retrieves the price
    for each token at various block heights, and asserts that a price is returned.

    Args:
        token: The address of the CToken to test.

    See Also:
        - :class:`~y.prices.lending.compound.CToken`
        - :func:`~y.prices.lending.compound.CToken.get_price`
    """
    print(token)
    ctoken = CToken(token)
    for block in blocks_for_contract(token):
        print(f"underlying per ctoken = {ctoken.underlying_per_ctoken(block)}")
        price = ctoken.get_price(block)
        assert price, "Failed to fetch price."
        print(f"                price = {price}")


@pytest.mark.parametrize("token", CTOKENS)
async def test_compound_pricing_async(token):
    """
    Test the asynchronous pricing of Compound tokens.

    This test iterates over a list of CToken addresses, retrieves the price
    for each token at various block heights asynchronously, and asserts that
    a price is returned.

    Args:
        token: The address of the CToken to test.

    See Also:
        - :class:`~y.prices.lending.compound.CToken`
        - :func:`~y.prices.lending.compound.CToken.get_price`
    """
    print(token)
    ctoken = CToken(token, asynchronous=True)
    for block in blocks_for_contract(token):
        print(f"underlying per ctoken = {await ctoken.underlying_per_ctoken(block)}")
        price = await compound.get_price(token, block)
        assert price, "Failed to fetch price."
        print(f"                price = {price}")
