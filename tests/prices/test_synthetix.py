import pytest
from tests.fixtures import mainnet_only
from y.contracts import Contract
from y.prices.synthetix import synthetix

SYNTHS = []
if synthetix:
    SYNTHS = synthetix.synths


@mainnet_only
def test_get_synths():
    assert len(synthetix.synths) >= 10


@mainnet_only
def test_synthetix_detection():
    sLINK = '0xbBC455cb4F1B9e4bFC4B73970d360c8f032EfEE6'
    assert sLINK in synthetix


@mainnet_only
@pytest.mark.parametrize('target', SYNTHS)
def test_synthetix_price(target):
    token = Contract(target).proxy()
    price = synthetix.get_price(token)
    print(price, Contract(target).currencyKey().decode().rstrip('\x00'))
    return price
