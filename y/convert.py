
import brownie.convert
from brownie.convert.datatypes import HexBytes

from y.datatypes import AnyAddressType


def to_address(address: AnyAddressType) -> str:
    if type(address) == int:
        return _int_to_address(address)
    return brownie.convert.to_address(address)

def _int_to_address(int_address: int) -> str:
    suffix = HexBytes(int_address).hex()[2:]
    padding = '0' * (40 - len(suffix))
    address = '0x' + padding + suffix
    return brownie.convert.to_address(address)
