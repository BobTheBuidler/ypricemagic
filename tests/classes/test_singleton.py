from random import randint

from brownie.convert.datatypes import EthAddress
from y import convert
from y.classes.common import ContractBase
from y.constants import WRAPPED_GAS_COIN
from y.contracts import Contract


def test_contract_singleton():
    """
    Test the singleton behavior of the `ContractBase` class.

    This test verifies that different representations of the same contract address
    are treated as equal instances of `ContractBase`. The `ChecksumASyncSingletonMeta`
    metaclass, which is the metaclass for `ContractBase`, ensures that only one instance
    of `ContractBase` exists for each unique contract address, regardless of how the
    address is formatted or represented.

    The test uses the `WRAPPED_GAS_COIN` constant as the contract address and creates
    several variations of it, including different case formats and types, to ensure
    that they all resolve to the same `ContractBase` instance.

    Note:
        `ChecksumASyncSingletonMeta` is the metaclass used by `ContractBase` to enforce
        singleton behavior.

    See Also:
        - :class:`y.classes.common.ContractBase`
        - :class:`y.contracts.Contract`
        - :data:`y.constants.WRAPPED_GAS_COIN`
    """
    token = WRAPPED_GAS_COIN
    variations = [
        token.lower(),
        token.upper(),
        convert.to_address(token),
        Contract(token),
        EthAddress(token.lower()),
    ]
    for variation in variations:
        assert ContractBase(WRAPPED_GAS_COIN) == ContractBase(
            variation
        ), "ContractBase singleton behavior is not working."
