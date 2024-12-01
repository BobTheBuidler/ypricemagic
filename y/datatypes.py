from typing import TYPE_CHECKING, Union

from brownie import Contract
from brownie.convert.datatypes import EthAddress, HexBytes
from eth_typing import AnyAddress, BlockNumber

if TYPE_CHECKING:
    from y.prices.dex.uniswap.v2 import UniswapV2Pool
    from y.prices.stable_swap.curve import CurvePool


Address = Union[str, HexBytes, AnyAddress, EthAddress]
"""
A union of types used to represent Ethereum addresses.

Examples:
    >>> address_str = "0x1234567890abcdef1234567890abcdef12345678"
    >>> address_hex = HexBytes("0x1234567890abcdef1234567890abcdef12345678")
    >>> address_any = AnyAddress("0x1234567890abcdef1234567890abcdef12345678")
    >>> address_eth = EthAddress("0x1234567890abcdef1234567890abcdef12345678")
"""

Block = Union[int, BlockNumber]
"""
A union of types used to represent block numbers as integers.

Examples:
    >>> block_int = 12345678
    >>> block_number = BlockNumber(12345678)
"""

AddressOrContract = Union[Address, Contract]
"""
A type alias representing either an Ethereum address or a contract object.
This can be an :data:`Address`, a :class:`~brownie.network.contract.Contract`, or its subclasses such as
:class:`~dank_mids.Contract` and :class:`~y.contracts.Contract`.

Examples:
    >>> address = "0x1234567890abcdef1234567890abcdef12345678"
    >>> contract = Contract.from_abi("MyContract", address, abi)
"""

AnyAddressType = Union[Address, Contract, int]
"""
A type alias representing any valid representation of an Ethereum address.
This can be an :data:`Address`, a :class:`~brownie.network.contract.Contract`, or an integer.

Examples:
    >>> any_address_str = "0x1234567890abcdef1234567890abcdef12345678"
    >>> any_address_contract = Contract.from_abi("MyContract", any_address_str, abi)
    >>> any_address_int = 12345678
"""

Pool = Union["UniswapV2Pool", "CurvePool"]
"""
A union of types representing liquidity pools.

Examples:
    >>> uniswap_pool = UniswapV2Pool("0xUniswapPoolAddress")
    >>> curve_pool = CurvePool("0xCurvePoolAddress")

See Also:
    - :class:`~y.prices.dex.uniswap.v2.UniswapV2Pool`
    - :class:`~y.prices.stable_swap.curve.CurvePool`
"""


class UsdValue(float):
    """
    Represents a USD value with custom string representation.

    Examples:
        >>> value = UsdValue(1234.5678)
        >>> str(value)
        '$1234.56780000'
    """

    def __str__(self) -> str:
        """
        Return a string representation of the USD value.
        The value is formatted as a USD value with 8 decimal places.
        """
        return f"${self:.8f}"


class UsdPrice(UsdValue):
    """
    Represents a USD price.

    Examples:
        >>> price = UsdPrice(1234.5678)
        >>> str(price)
        '$1234.56780000'
    """
