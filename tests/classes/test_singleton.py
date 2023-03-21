
from random import randint

from brownie.convert.datatypes import EthAddress
from y import convert
from y.classes.common import ContractBase
from y.constants import WRAPPED_GAS_COIN
from y.contracts import Contract


def test_contract_singleton():
    token = WRAPPED_GAS_COIN
    variations = [token.lower(), token.upper(), convert.to_address(token), Contract(token), EthAddress(token.lower())]
    for variation in variations:
        assert ContractBase(WRAPPED_GAS_COIN) == ContractBase(variation), 'ContractSingleton metaclass is not working.'
