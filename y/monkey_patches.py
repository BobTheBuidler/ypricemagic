import brownie.convert
import checksum_dict._utils
import dank_mids.brownie_patch.call
import eth_event.main
import eth_utils
import evmspec.data._main
import multicall.call
import web3._utils as web3_utils
import web3.main as web3_main
import web3.middleware as web3_middleware

import y.convert


def monkey_patch_checksum_cache():
    """
    Monkey patch dependency checksums with faster versions.

    This function replaces the default checksumming functions in various libraries
    with a faster implementation using `to_address`. This improves performance
    by utilizing caching and optimized checksumming.

    See Also:
        - :func:`to_address` for the checksumming process.
    """
    # this monkey patches brownie's convert.to_address with our lru_cache
    brownie.convert.to_address = y.convert.to_address

    # this monkey patches checksum_dict's checksumming with our lru_cache
    checksum_dict._utils.to_checksum_address = y.convert.to_address

    # this monkey patches the dank_mids brownie patch's checksums with our lru_cache
    dank_mids.brownie_patch.call.to_checksum_address = y.convert.to_address

    # this monkey patches eth_event's address checksumming with our lru_cache
    eth_event.main.to_checksum_address = y.convert.to_address

    # this monkey patches brownie's EthAddress class with faster execution
    eth_utils.to_checksum_address = y.convert.to_address

    # this monkey patches something else I don't remember now with faster execution
    eth_utils.address.to_checksum_address = y.convert.to_address

    # this monkey patches evmspec's Address decode hook with our lru cache
    evmspec.data._main.to_checksum_address = y.convert.to_address

    # this monkey patches multicall.Call.target checksumming with our lru cache
    multicall.call.to_checksum_address = y.convert.to_address

    # this monkey patches all checksums in web3py with faster execution
    web3_main.to_checksum_address = y.convert.to_address
    web3_utils.ens.to_checksum_address = y.convert.to_address
    web3_utils.method_formatters.to_checksum_address = y.convert.to_address
    web3_utils.normalizers.to_checksum_address = y.convert.to_address
    web3_middleware.signing.to_checksum_address = y.convert.to_address

    try:
        import web3.utils.address as web3_address

        web3_address.to_checksum_address = y.convert.to_address
    except ModuleNotFoundError:
        # youre on an older web3py, no monkey patch for you
        pass

    try:
        import ens.ens

        ens.ens.to_checksum_address = y.convert.to_address
    except ModuleNotFoundError:
        # youre on an older web3py, no monkey patch for you
        pass

    try:
        import ens.async_ens

        ens.async_ens.to_checksum_address = y.convert.to_address
    except ModuleNotFoundError:
        # youre on an older web3py, no monkey patch for you
        pass
