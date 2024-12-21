from typing import final

import evmspec


@final
class Log(
    evmspec.Log, frozen=True, kw_only=True, array_like=True, forbid_unknown_fields=True
):
    """
    Extends :class:`evmspec.Log` with additional configuration for immutability,
    keyword-only arguments, and array-like encoding behavior using :class:`msgspec.Struct`.

    This class is designed to behave like a tuple specifically during `msgspec.json`
    encoding and decoding, allowing instances to be encoded as tuples instead of
    dictionaries. This approach optimizes space usage since the keys are known and
    fixed, making it efficient for scenarios where space efficiency is critical.
    The `array_like=True` parameter from :class:`msgspec.Struct` is utilized to achieve
    this behavior during JSON serialization.

    Examples:
        Creating a Log instance with keyword-only arguments:

        >>> log_entry = Log(address='0x...', topics=['0x...'], data='0x...')
        >>> print(log_entry)

        Accessing log entry as a tuple during JSON encoding:

        >>> import msgspec.json
        >>> log_tuple = msgspec.json.encode(log_entry)
        >>> print(log_tuple)

    See Also:
        - :class:`evmspec.Log` for the base class implementation.
        - :class:`msgspec.Struct` for details on the `array_like` feature.
    """
