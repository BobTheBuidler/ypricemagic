import pytest
from multicall.utils import await_awaitable

from tests.fixtures import mainnet_only
from y.exceptions import UnsupportedNetwork
from y.prices.synthetix import Synthetix

try:
    sync_synthetix = Synthetix()
    async_synthetix = Synthetix(asynchronous=True)
    SYNTHS = sync_synthetix.synths
except UnsupportedNetwork:
    SYNTHS = []


@mainnet_only
def test_get_synths():
    assert len(sync_synthetix.synths) >= 10


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_get_synths_async():
    assert len(await async_synthetix.synths) >= 10


@mainnet_only
def test_synthetix_detection():
    sLINK = "0xbBC455cb4F1B9e4bFC4B73970d360c8f032EfEE6"
    assert sync_synthetix.is_synth(sLINK) == True


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_synthetix_detection_async():
    sLINK = "0xbBC455cb4F1B9e4bFC4B73970d360c8f032EfEE6"
    assert await async_synthetix.is_synth(sLINK) == True


@pytest.mark.parametrize("token", SYNTHS)
def test_synthetix_price(token):
    assert async_synthetix.get_price(token, sync=True) == await_awaitable(
        sync_synthetix.get_price(token, sync=False)
    )
