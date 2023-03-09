
import pytest
from tests.fixtures import mutate_address, mutate_contract
from tests.prices.lending.test_aave import ATOKENS
from tests.prices.lending.test_compound import CTOKENS
from tests.prices.test_chainlink import FEEDS
from tests.prices.test_popsicle import POPSICLES
from tests.prices.test_synthetix import SYNTHS
from tests.test_constants import STABLECOINS
from y import convert
from y.constants import EEE_ADDRESS, WRAPPED_GAS_COIN
from y.prices.utils.buckets import check_bucket


#@pytest.mark.parametrize('token',ATOKENS)
#def test_check_bucket_aave(token):
    #assert check_bucket(token) == 'atoken'

@pytest.mark.parametrize('token',ATOKENS)
@pytest.mark.asyncio_cooperative
async def test_check_bucket_aave(token):
    assert await check_bucket(token, sync=False) == 'atoken'

@pytest.mark.parametrize('token',FEEDS)
@pytest.mark.asyncio_cooperative
async def test_check_bucket_chainlink(token):
    if convert.to_address(token) in [stable for stable in STABLECOINS if not isinstance(stable,int)]:
        pytest.skip(f'Not applicable to stablecoins.')
    if token in mutate_contract(WRAPPED_GAS_COIN) + mutate_address(EEE_ADDRESS):
        pytest.skip(f'Not applicable to native token.')
    assert await check_bucket(token, sync=False) == 'chainlink feed'

@pytest.mark.parametrize('token',CTOKENS)
@pytest.mark.asyncio_cooperative
async def test_check_bucket_compound(token):
    assert await check_bucket(token, sync=False) == 'compound'

@pytest.mark.parametrize('token',POPSICLES)
@pytest.mark.asyncio_cooperative
async def test_check_bucket_popsicle(token):
    assert await check_bucket(token, sync=False) == 'popsicle'

@pytest.mark.parametrize('token',STABLECOINS)
@pytest.mark.asyncio_cooperative
async def test_check_bucket_stablecoins(token):
    assert await check_bucket(token, sync=False) == 'stable usd'

@pytest.mark.parametrize('token',SYNTHS)
@pytest.mark.asyncio_cooperative
async def test_check_bucket_synthetix(token):
    assert await check_bucket(token, sync=False) == 'synthetix'
