
import brownie.convert
from brownie.convert.datatypes import HexBytes

from y.typing import AnyAddressType

def to_address(address: AnyAddressType) -> str:
    if type(address) == int:
        address = HexBytes(address)
    return brownie.convert.to_address(address)