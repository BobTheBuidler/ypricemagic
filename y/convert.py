from functools import lru_cache
from typing import Final, Optional, Set

import a_sync
import cchecksum
import hexbytes
from eth_typing import AnyAddress, ChecksumAddress, HexAddress

from y import ENVIRONMENT_VARIABLES as ENVS
from y.datatypes import AnyAddressType


HexBytes: Final = hexbytes.HexBytes

to_checksum_address: Final = cchecksum.to_checksum_address


@lru_cache(maxsize=ENVS.CHECKSUM_CACHE_MAXSIZE)  # type: ignore [call-overload]
def checksum(address: AnyAddress) -> ChecksumAddress:
    """Convert an address to its checksummed format.

    This function uses the `to_checksum_address` function to convert an Ethereum address
    to its checksummed format. If the address is invalid, a `ValueError` is raised.

    Args:
        address: The Ethereum address to be checksummed.

    Raises:
        ValueError: If the provided address is not a valid Ethereum address.

    Returns:
        The checksummed Ethereum address.

    Examples:
        >>> checksum("0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe")
        '0xDe0B295669a9FD93d5F28D9Ec85E40f4cb697BAe'

    See Also:
        - :func:`to_checksum_address` for the underlying implementation.
    """
    try:
        return to_checksum_address(address)
    except ValueError:
        raise ValueError(f"{repr(address)} is not a valid ETH address") from None


def to_address(address: AnyAddressType) -> ChecksumAddress:
    """Convert an address to a checksummed address, with caching.

    This function normalizes the input address to a string, checks if it is already
    checksummed and cached, and if not, computes the checksummed address and caches it.

    Args:
        address: The Ethereum address to be converted.

    Returns:
        The checksummed Ethereum address.

    Examples:
        >>> to_address("0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe")
        '0xDe0B295669a9FD93d5F28D9Ec85E40f4cb697BAe'

    See Also:
        - :func:`checksum` for the checksumming process.
        - :func:`__normalize_input_to_string` for input normalization.
    """
    address = __normalize_input_to_string(address)
    if checksummed := __get_checksum_from_cache(address):
        return checksummed
    checksummed = checksum(address)
    __cache_if_is_checksummed(address, checksummed)
    return checksummed  # type: ignore [return-value]


_checksum_thread: Final = a_sync.ThreadPoolExecutor(1)


async def to_address_async(address: AnyAddressType) -> ChecksumAddress:
    """Asynchronously convert an address to a checksummed address, with caching.

    This function normalizes the input address to a string, checks if it is already
    checksummed and cached, and if not, computes the checksummed address asynchronously
    and caches it.

    Args:
        address: The Ethereum address to be converted.

    Returns:
        The checksummed Ethereum address.

    Examples:
        >>> await to_address_async("0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe")
        '0xDe0B295669a9FD93d5F28D9Ec85E40f4cb697BAe'

    See Also:
        - :func:`checksum` for the checksumming process.
        - :func:`__normalize_input_to_string` for input normalization.
    """
    normalized = __normalize_input_to_string(address)
    if checksummed := __get_checksum_from_cache(normalized):
        return checksummed
    checksummed = await _checksum_thread.run(checksum, normalized)
    __cache_if_is_checksummed(normalized, checksummed)
    return checksummed


_is_checksummed: Final[Set[ChecksumAddress]] = set()
_is_not_checksummed: Final[Set[HexAddress]] = set()


def __get_checksum_from_cache(address: HexAddress) -> Optional[ChecksumAddress]:
    """Retrieve a checksummed address from the cache if available.

    This function checks if the given address is already known to be checksummed,
    and if so, returns the address. If the address is known to not be checksummed,
    it computes and returns the checksummed address.

    Args:
        address: The Ethereum address to check in the cache.

    Returns:
        The cached checksummed address if available, otherwise None.

    See Also:
        - :func:`checksum` for the checksumming process.
    """
    if address in _is_checksummed:
        return address  # type: ignore [return-value]
    elif address in _is_not_checksummed:
        # The checksum value is already in the lru-cache, there
        # is no reason to dispatch this function call to a thread.
        return checksum(address)
    else:
        return None


def __cache_if_is_checksummed(address: HexAddress, checksummed: ChecksumAddress) -> None:
    """Cache the address based on whether it is checksummed.

    This function adds the address to the `_is_checksummed` set if it is already
    checksummed, otherwise it adds it to the `_is_not_checksummed` set.

    Args:
        address: The original Ethereum address.
        checksummed: The checksummed Ethereum address.
    """
    if address == checksummed:
        _is_checksummed.add(address)
    else:
        _is_not_checksummed.add(address)


def __normalize_input_to_string(address: AnyAddressType) -> HexAddress:
    r"""Normalize the input address to a string format.

    This function converts the input address to a string format, handling different
    types such as strings, bytes, and integers. The function ensures that the address
    is in a consistent string format for further processing.

    Args:
        address: The Ethereum address to be normalized.

    Returns:
        The normalized address as a string.

    Examples:
        >>> __normalize_input_to_string("0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe")
        '0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe'
        >>> __normalize_input_to_string(b'\xde\x0b)e\x66\x9a\x9f\xd9=_(\xd9\xec\x85\xe4\x0fL\xb6\x97\xba\xe')
        '0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae'
        >>> __normalize_input_to_string(123456789)
        '0x000000000000000000000000000000000000075b'

    See Also:
        - :class:`HexBytes` for handling byte conversions.
    """
    address_type = type(address)
    if address_type is str:
        return address  # type: ignore [return-value]
    elif issubclass(address_type, bytes):
        return (
            address.hex()  # type: ignore [union-attr, return-value]
            if address_type.__name__ == "HexBytes"
            else HexBytes(address).hex()
        )
    elif address_type is int:
        return _int_to_address(address)  # type: ignore [arg-type]
    else:
        return str(address)  # type: ignore [return-value]


def _int_to_address(int_address: int) -> HexAddress:
    """Convert an integer to an Ethereum address in hexadecimal format.

    This function converts an integer to a hexadecimal Ethereum address, ensuring
    it is properly padded to 40 characters.

    Args:
        int_address: The integer representation of the Ethereum address.

    Returns:
        The Ethereum address in hexadecimal format.

    Examples:
        >>> _int_to_address(123456789)
        '0x000000000000000000000000000000000000075b'
    """
    hex_value = HexBytes(int_address).hex()[2:]
    padding = "0" * (40 - len(hex_value))
    return f"0x{padding}{hex_value}"  # type: ignore [return-value]
