from functools import lru_cache
from typing import Set

import brownie.convert
import checksum_dict._key
import eth_event.main
import eth_utils
import evmspec.data
from brownie.convert.datatypes import EthAddress, HexBytes
from checksum_dict import to_checksum_address
from eth_typing import ChecksumAddress, HexAddress

from y import ENVIRONMENT_VARIABLES as ENVS
from y.datatypes import AnyAddressType


@lru_cache(maxsize=ENVS.CHECKSUM_CACHE_MAXSIZE)
def checksum(address: AnyAddressType) -> ChecksumAddress:
    try:
        return to_checksum_address(address)
    except ValueError:
        raise ValueError(f"'{address}' is not a valid ETH address") from None


def to_address(address: AnyAddressType) -> ChecksumAddress:
    if isinstance(address, bytes):
        address = (
            address.hex()
            if type(address).__name__ == "HexBytes"
            else HexBytes(address).hex()
        )
    elif type(address) == int:
        address = _int_to_address(address)
    else:
        address = str(address)

    if address in _is_checksummed:
        return address
    elif address in _is_not_checksummed:
        return checksum(address)

    try:
        checksummed = to_checksum_address(address)
    except ValueError:
        raise ValueError(f"'{address}' is not a valid ETH address") from None

    if address == checksummed:
        _is_checksummed.add(address)
    else:
        _is_not_checksummed.add(address)
    return checksummed


_is_checksummed: Set[HexAddress] = set()
_is_not_checksummed: Set[HexAddress] = set()


def _int_to_address(int_address: int) -> HexAddress:
    hex_value = HexBytes(int_address).hex()[2:]
    padding = "0" * (40 - len(hex_value))
    return f"0x{padding}{hex_value}"


def _monkey_patch_dependencies():
    """
    Monkey patch dependency checksums with faster versions.
    """
    # this monkey patches checksum_dict's checksumming with our lru_cache
    checksum_dict._key.to_checksum_address = to_address

    # this monkey patches eth_event's address checksumming with our lru_cache
    eth_event.main.to_checksum_address = to_address

    # this monkey patches brownie's convert.to_address with our lru_cache
    brownie.convert.to_address = to_address

    # this monkey patches evmspec's Address decode hook with our lru cache
    evmspec.data.to_checksum_address = to_address

    # y.convert.to_address depends on brownie.convert.to_address which depends on eth_utils.to_checksum_address
    # so we cannot overwrite eth_utils.to_checksum_address with y.convert.to_address like we do for eth_event
    # or we will create a circular dependency

    # this monkey patches brownie's EthAddress class with faster execution
    eth_utils.to_checksum_address = to_checksum_address

    # this monkey patches something else I don't remember now with faster execution
    eth_utils.address.to_checksum_address = to_checksum_address
