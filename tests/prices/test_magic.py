
from typing import List

from brownie import chain
import pytest
from tests.prices.dex.test_uniswap import V1_TOKENS, V2_TOKENS
from tests.prices.lending.test_aave import ATOKENS
from tests.prices.lending.test_compound import CTOKENS
from tests.prices.test_chainlink import FEEDS
from tests.prices.test_popsicle import POPSICLES
from tests.prices.test_synthetix import SYNTHS
from y import convert
from y.contracts import contract_creation_block
from y.exceptions import CantFetchParam, PriceError
from y.prices import magic


START_TESTS_AT_BLOCK = 11_000_000
INCREMENT = 200_000
NUM_ITERATIONS = (chain.height - START_TESTS_AT_BLOCK) // INCREMENT
BLOCKS = [START_TESTS_AT_BLOCK + INCREMENT * i for i in range(NUM_ITERATIONS)]

ALL_TOKENS: List = V1_TOKENS + V2_TOKENS + ATOKENS + CTOKENS + FEEDS + POPSICLES + SYNTHS

# subtraction underflow, not relevant to point of test
ALL_TOKENS.remove('0x892B14321a4FCba80669aE30Bd0cd99a7ECF6aC0')
ALL_TOKENS.remove('0x892B14321a4FCba80669aE30Bd0cd99a7ECF6aC0') 
ALL_TOKENS.remove('0x892b14321a4fcba80669ae30bd0cd99a7ecf6ac0')
ALL_TOKENS.remove('0x892B14321A4FCBA80669AE30BD0CD99A7ECF6AC0')

# ibibBTC, not relevant to point of test
ALL_TOKENS.remove('0x2a867fd776b83e1bd4e13c6611afd2f6af07ea6d') 
ALL_TOKENS.remove('0x2A867FD776B83E1BD4E13C6611AFD2F6AF07EA6D')
ALL_TOKENS.remove('0x2A867fd776B83e1bd4e13C6611AFd2F6af07EA6D')
ALL_TOKENS.remove('0x2A867fd776B83e1bd4e13C6611AFd2F6af07EA6D')

# multicall aggregate failed, not relevant to point of test
ALL_TOKENS.remove('0x4ee15f44c6f0d8d1136c83efd2e8e4ac768954c6')
ALL_TOKENS.remove('0x4EE15F44C6F0D8D1136C83EFD2E8E4AC768954C6')
ALL_TOKENS.remove('0x4EE15f44c6F0d8d1136c83EfD2e8E4AC768954c6')
ALL_TOKENS.remove('0x4EE15f44c6F0d8d1136c83EfD2e8E4AC768954c6')
ALL_TOKENS.remove('0x9baf8a5236d44ac410c0186fe39178d5aad0bb87')
ALL_TOKENS.remove('0x9BAF8A5236D44AC410C0186FE39178D5AAD0BB87')
ALL_TOKENS.remove('0x9baF8a5236d44AC410c0186Fe39178d5AAD0Bb87')
ALL_TOKENS.remove('0x9baF8a5236d44AC410c0186Fe39178d5AAD0Bb87')


@pytest.mark.parametrize('block', BLOCKS)
def test_get_prices(block):
    tokens = relevant_tokens(ALL_TOKENS, block)
    checked_separately = [get_price(token, block) for token in tokens]
    checked_together = magic.get_prices(tokens, block, fail_to_None=True)
    for i in range(len(checked_together)):
        assert checked_together[i] == checked_separately[i], f'magic.get_prices price discrepancy for {tokens[i]}'

def get_price(token, block):
    """ This is just to diagnose issues with the test itself. We may need to exclude certain tokens. """
    try:
        return magic.get_price(token, block, fail_to_None=True)
    except CantFetchParam as e:
        raise CantFetchParam(token, str(e))
    except PriceError:
        return None
    except TypeError as e:
        raise TypeError(token, str(e))
    except ValueError as e:
        raise ValueError(token, str(e))

def relevant_tokens(tokens, block):
    return [
        token for token in tokens
        if contract_creation_block(convert.to_address(token))
        and contract_creation_block(convert.to_address(token)) <= block
    ]
