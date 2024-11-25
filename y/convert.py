from functools import lru_cache

from brownie.convert.datatypes import EthAddress, HexBytes
from eth_typing import ChecksumAddress, HexAddress

from y import ENVIRONMENT_VARIABLES as ENVS
from y.datatypes import AnyAddressType


@lru_cache(maxsize=ENVS.CHECKSUM_CACHE_MAXSIZE)
def to_address(address: AnyAddressType) -> ChecksumAddress:
    if type(address) == int:
        address = _int_to_address(address)
    return str(EthAddress(address))


def _int_to_address(int_address: int) -> HexAddress:
    hex_value = HexBytes(int_address).hex()[2:]
    padding = "0" * (40 - len(hex_value))
    return f"0x{padding}{hex_value}"
