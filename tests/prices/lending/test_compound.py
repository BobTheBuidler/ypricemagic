
import pytest

from tests.fixtures import blocks_for_contract
from y.prices.lending.compound import CToken, compound

CTOKENS = [ctoken.address for troller in compound.trollers.values() for ctoken in troller.__markets__(sync=True)]

@pytest.mark.parametrize('token', CTOKENS)
def test_compound_pricing_sync(token):
    print(token)
    #if convert.to_address(token) == '0x892B14321a4FCba80669aE30Bd0cd99a7ECF6aC0':
    #    continue  # creth is broken
    ctoken = CToken(token)
    for block in blocks_for_contract(token):
        print(f'underlying per ctoken = {ctoken.underlying_per_ctoken(block)}')
        price = ctoken.get_price(block)
        assert price, 'Failed to fetch price.'
        print(f'                price = {price}')

@pytest.mark.parametrize('token', CTOKENS)
async def test_compound_pricing_async(token):
    print(token)
    #if convert.to_address(token) == '0x892B14321a4FCba80669aE30Bd0cd99a7ECF6aC0':
    #    continue  # creth is broken
    ctoken = CToken(token, asynchronous=True)
    for block in blocks_for_contract(token):
        print(f'underlying per ctoken = {await ctoken.underlying_per_ctoken(block)}')
        price = await compound.get_price(token, block)
        assert price, 'Failed to fetch price.'
        print(f'                price = {price}')
