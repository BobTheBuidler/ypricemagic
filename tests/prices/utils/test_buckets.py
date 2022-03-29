
import pytest
from tests.prices.lending.test_aave import ATOKENS
from tests.prices.lending.test_compound import CTOKENS
from tests.prices.test_chainlink import FEEDS
from tests.prices.test_popsicle import POPSICLES
from tests.prices.test_synthetix import SYNTHS
from y.prices.utils.buckets import check_bucket


@pytest.mark.parametrize('token',ATOKENS)
def test_check_bucket_aave(token):
    assert check_bucket(token) == 'atoken'

@pytest.mark.parametrize('token',FEEDS)
def test_check_bucket_chainlink(token):
    assert check_bucket(token) == 'chainlink feed'

@pytest.mark.parametrize('token',CTOKENS)
def test_check_bucket_compound(token):
    assert check_bucket(token) == 'compound'

@pytest.mark.parametrize('token',POPSICLES)
def test_check_bucket_popsicle(token):
    assert check_bucket(token) == 'popsicle'

@pytest.mark.parametrize('token',SYNTHS)
def test_check_bucket_synthetix(token):
    assert check_bucket(token) == 'synthetix'
