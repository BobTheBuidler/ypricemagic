import pytest
from tests.constants import STABLECOINS
from tests.fixtures import blocks_for_contract, mutate_tokens
from y.classes.common import ERC20
from y.constants import WRAPPED_GAS_COIN, wbtc

TOKENS = STABLECOINS + mutate_tokens([WRAPPED_GAS_COIN, wbtc.address])

@pytest.mark.parametrize('token',TOKENS)
def test_erc20(token):
    token = ERC20(token)
    assert token.contract, f'Cannot fetch contract for token {token}'
    assert token.build_name, f'Cannot fetch build name for token {token}'
    assert token.symbol, f'Cannot fetch symbol for token {token}'
    assert token.name, f'Cannot fetch name for token {token}'
    assert token.decimals, f'Cannot fetch decimals for token {token}'
    assert token.scale, f'Cannot fetch scale for token {token}'
    assert 10 ** token.decimals == token.scale, f'Incorrect scale fetched for token {token}'
    assert token.total_supply() is not None, f'Cannot fetch total supply for token {token}'
    assert token.total_supply_readable() is not None, f'Cannot fetch total supply readable for token {token}'
    assert token.total_supply() / token.scale == token.total_supply_readable(), f'Incorrect total supply readable for token {token}'
    assert token.price(), f'Cannot fetch price for token {token}'

    for block in blocks_for_contract(token.address):
        assert token._decimals(block), f'Cannot fetch decimals for token {token}'
        assert token._scale(block), f'Cannot fetch scale for token {token}'
        assert token.total_supply(block) is not None, f'Cannot fetch total supply for token {token}'
        assert token.total_supply_readable(block) is not None, f'Cannot fetch total supply readable for token {token}'
        assert token.total_supply(block) / token._scale(block) == token.total_supply_readable(block), f'Incorrect total supply readable for token {token}'
        assert token.price(block), f'Cannot fetch price for token {token}'
