
import pytest
from brownie import chain
from tests.fixtures import blocks_for_contract, mutate_address
from y.networks import Network
from y.prices import popsicle
from y.constants import WRAPPED_GAS_COIN

POPSICLES = {
    Network.Mainnet: [
        "0xd2C5A739ebfE3E00CFa88A51749d367d7c496CCf",
    ],
}.get(chain.id, [])

POPSICLES = [mutation for address in POPSICLES for mutation in mutate_address(address)]

@pytest.mark.parametrize('token',POPSICLES)
def test_popsicle_get_price(token):
    assert popsicle.is_popsicle_lp(token), 'Popsicle LP not recognized.'
    blocks = blocks_for_contract(token, 10)
    for block in blocks:
        assert popsicle.get_price(token, block), 'Failed to fetch price.'

def test_non_popsicle():
    assert not popsicle.is_popsicle_lp(WRAPPED_GAS_COIN), 'Token incorrectly recognized as Popsicle LP.'
    with pytest.raises(TypeError):
        popsicle.get_price(WRAPPED_GAS_COIN)
