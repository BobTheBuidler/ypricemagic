from functools import lru_cache
from typing import Optional, Set

import a_sync
import brownie.convert
import checksum_dict._key
import dank_mids.brownie_patch.call
import eth_event.main
import eth_utils
import evmspec.data._main
import multicall.call
import web3._utils as web3_utils
import web3.main as web3_main
import web3.middleware as web3_middleware
from brownie.convert.datatypes import HexBytes
from cchecksum import to_checksum_address
from eth_typing import ChecksumAddress, HexAddress

from y import ENVIRONMENT_VARIABLES as ENVS
from y.datatypes import AnyAddressType


@lru_cache(maxsize=ENVS.CHECKSUM_CACHE_MAXSIZE)
def checksum(address: AnyAddressType) -> ChecksumAddress:
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
        raise ValueError(f"'{address}' is not a valid ETH address") from None


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
    return checksummed


_checksum_thread = a_sync.ThreadPoolExecutor(1)


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
    address = __normalize_input_to_string(address)
    if checksummed := __get_checksum_from_cache(address):
        return checksummed
    checksummed = await _checksum_thread.run(checksum, address)
    __cache_if_is_checksummed(address, checksummed)
    return checksummed


_is_checksummed: Set[HexAddress] = set()
_is_not_checksummed: Set[HexAddress] = set()


def __get_checksum_from_cache(address: AnyAddressType) -> Optional[ChecksumAddress]:
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
        return address
    elif address in _is_not_checksummed:
        # The checksum value is already in the lru-cache, there
        # is no reason to dispatch this function call to a thread.
        return checksum(address)


def __cache_if_is_checksummed(
    address: HexAddress, checksummed: ChecksumAddress
) -> None:
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
        return address
    elif issubclass(address_type, bytes):
        return (
            address.hex()
            if address_type.__name__ == "HexBytes"
            else HexBytes(address).hex()
        )
    elif address_type is int:
        return _int_to_address(address)
    else:
        return str(address)


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
    return f"0x{padding}{hex_value}"


def _monkey_patch_dependencies():
    """
    Monkey patch dependency checksums with faster versions.

    This function replaces the default checksumming functions in various libraries
    with a faster implementation using `to_address`. This improves performance
    by utilizing caching and optimized checksumming.

    See Also:
        - :func:`to_address` for the checksumming process.
    """
    # this monkey patches brownie's convert.to_address with our lru_cache
    brownie.convert.to_address = to_address

    # this monkey patches checksum_dict's checksumming with our lru_cache
    checksum_dict._key.to_checksum_address = to_address

    # this monkey patches the dank_mids brownie patch's checksums with our lru_cache
    dank_mids.brownie_patch.call.to_checksum_address = to_address

    # this monkey patches eth_event's address checksumming with our lru_cache
    eth_event.main.to_checksum_address = to_address

    # this monkey patches brownie's EthAddress class with faster execution
    eth_utils.to_checksum_address = to_address

    # this monkey patches something else I don't remember now with faster execution
    eth_utils.address.to_checksum_address = to_address

    # this monkey patches evmspec's Address decode hook with our lru cache
    evmspec.data._main.to_checksum_address = to_address

    # this monkey patches multicall.Call.target checksumming with our lru cache
    multicall.call.to_checksum_address = to_address

    # this monkey patches all checksums in web3py with faster execution
    web3_main.to_checksum_address = to_address
    web3_utils.ens.to_checksum_address = to_address
    web3_utils.method_formatters.to_checksum_address = to_address
    web3_utils.normalizers.to_checksum_address = to_address
    web3_middleware.signing.to_checksum_address = to_address

    try:
        import web3.utils.address as web3_address

        web3_address.to_checksum_address = to_address
    except ModuleNotFoundError:
        # youre on an older web3py, no monkey patch for you
        pass

    try:
        import ens.ens

        ens.ens.to_checksum_address = to_address
    except ModuleNotFoundError:
        # youre on an older web3py, no monkey patch for you
        pass

    try:
        import ens.async_ens

        ens.async_ens.to_checksum_address = to_address
    except ModuleNotFoundError:
        # youre on an older web3py, no monkey patch for you
        pass
