import pytest
from tests.fixtures import blocks_for_contract, mutate_addresses
from y.classes.common import ERC20
from y.prices.lending.compound import CToken, compound

CTOKENS = mutate_addresses([
    ctoken.address
    for troller in compound.trollers.values()
    for ctoken in troller.markets
])

@pytest.mark.parametrize('token',CTOKENS)
def test_compound_pricing(token):
    print(token)
    #if convert.to_address(token) == '0x892B14321a4FCba80669aE30Bd0cd99a7ECF6aC0':
    #    continue  # creth is broken
    ctoken = CToken(token)
    for block in blocks_for_contract(token):
        print(f'underlying per ctoken = {ctoken.underlying_per_ctoken(block)}')
        price = compound.get_price(token, block)
        assert price, 'Failed to fetch price.'
        print(f'                price = {price}')
