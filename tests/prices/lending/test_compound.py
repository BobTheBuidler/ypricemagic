import pytest
from tests.fixtures import blocks_for_contract, mutate_address
from y.classes.common import ERC20
from y.prices.lending.compound import CToken, compound

CTOKENS = [
    mutation
    for troller in compound.trollers.values()
    for address in troller.markets
    for mutation in mutate_address(address)
]

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


def test_compound_cap():
    for comp in compound.trollers.values():
        print(comp.key)
        total = 0
        for token in comp.markets:
            if token == '0x892B14321a4FCba80669aE30Bd0cd99a7ECF6aC0':
                continue  # creth is broken
            
            price = compound.get_price(token)
            supply = ERC20(token).total_supply_readable()
            print(f'  {token.name} {supply:,.0f} x {price:,.2f} = {supply * price:,.0f}')
            total += supply * price

        print(f'{comp.key} = {total:,.0f}')
