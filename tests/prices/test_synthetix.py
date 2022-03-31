import pytest
from tests.fixtures import mainnet_only, mutate_tokens
from y.prices.synthetix import synthetix

SYNTHS = mutate_tokens(synthetix.synths if synthetix else ())


@mainnet_only
def test_get_synths():
    assert len(synthetix.synths) >= 10


@mainnet_only
def test_synthetix_detection():
    sLINK = '0xbBC455cb4F1B9e4bFC4B73970d360c8f032EfEE6'
    assert sLINK in synthetix


@pytest.mark.parametrize('token', SYNTHS)
def test_synthetix_price(token):
    price = synthetix.get_price(token)
    print(price)
    return price
