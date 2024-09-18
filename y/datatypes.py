
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
"""

Block = Union[int, BlockNumber]
"""
A union of types used to represent block numbers as integers.
"""

AddressOrContract = Union[Address,Contract]

AnyAddressType = Union[Address, Contract, int]
"""
A type alias representing any valid representation of an Ethereum address.
This can be an Address, a :class:`~y.Contract`, or an integer.
"""

Pool = Union["UniswapV2Pool", "CurvePool"]
"""
A union of types representing liquidity pools.
"""

class UsdValue(float):
    """
    Represents a USD value with custom string representation.
    """
    
    def __str__(self) -> str:
        """
        Return a string representation of the USD value.

        Returns:
            A string formatted as a USD value with 8 decimal places.
        """
        return f'${self:.8f}'

class UsdPrice(UsdValue):
    """
    Represents a USD price.
    """
