import pytest
from multicall.utils import await_awaitable
from tests.fixtures import mainnet_only, mutate_tokens
from y.prices.synthetix import synthetix

SYNTHS = mutate_tokens(await_awaitable(synthetix.synths) if synthetix else ())


@mainnet_only
def test_get_synths():
    assert len(synthetix.synths) >= 10


@mainnet_only
def test_synthetix_detection():
    sLINK = '0xbBC455cb4F1B9e4bFC4B73970d360c8f032EfEE6'
    assert await_awaitable(synthetix.is_synth(sLINK))


@pytest.mark.parametrize('token', SYNTHS)
def test_synthetix_price(token):
    assert synthetix.get_price(token)
