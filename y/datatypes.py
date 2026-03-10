from dataclasses import dataclass
from typing import TYPE_CHECKING, Union

import evmspec.data
from brownie import Contract
from brownie.convert.datatypes import EthAddress, HexBytes
from eth_typing import AnyAddress, BlockNumber

if TYPE_CHECKING:
    from y.prices.dex.balancer.v2 import BalancerV2Pool
    from y.prices.dex.uniswap.v2 import UniswapV2Pool
    from y.prices.stable_swap.curve import CurvePool


Address = Union[str, HexBytes, AnyAddress, evmspec.data.Address, EthAddress]
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

Pool = Union["UniswapV2Pool", "CurvePool", "BalancerV2Pool"]
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


@dataclass
class PriceStep:
    """
    Represents a single step in a price derivation path.

    Each step captures how a price was derived at a particular stage of resolution,
    including the source, input/output tokens, pool address (if applicable), and
    the intermediate price.

    Attributes:
        source: The pricing source (e.g., 'chainlink', 'uniswap_v3', 'curve').
        input_token: The address of the input token for this step.
        output_token: The address or symbol of the output token for this step.
        pool: The pool address used for pricing, if applicable.
        price: The price at this step.

    Examples:
        >>> step = PriceStep(
        ...     source='chainlink',
        ...     input_token='WETH',
        ...     output_token='USD',
        ...     pool=None,
        ...     price=1.0
        ... )
        >>> step.source
        'chainlink'
    """

    source: str
    input_token: str
    output_token: str
    pool: str | None
    price: float

    def __repr__(self) -> str:
        """
        Return a concise string representation of the price step.

        Shows source, truncated input/output token addresses, and pool (if present).
        """
        # Truncate long addresses for readability
        inp = (
            self.input_token[:6] + "..." + self.input_token[-4:]
            if len(self.input_token) > 12
            else self.input_token
        )
        out = (
            self.output_token[:6] + "..." + self.output_token[-4:]
            if len(self.output_token) > 12
            else self.output_token
        )
        pool_str = f", pool={self.pool[:6]}...{self.pool[-4:]}" if self.pool else ""
        return f"PriceStep(source='{self.source}', input_token='{inp}', output_token='{out}'{pool_str})"


@dataclass
class PriceResult:
    """
    Represents the result of a price resolution with derivation path information.

    PriceResult wraps the final price with the path of pricing steps that were used
    to derive it. This enables callers to understand how a price was obtained.

    Attributes:
        price: The final price (typically UsdPrice for USD-denominated prices).
        path: List of PriceStep objects showing the derivation path.

    Examples:
        >>> result = PriceResult(price=UsdPrice(1234.56), path=[])
        >>> bool(result)
        True
        >>> float(result)
        1234.56
        >>> result_zero = PriceResult(price=UsdPrice(0), path=[])
        >>> bool(result_zero)
        False
    """

    price: float
    path: list[PriceStep]

    def __bool__(self) -> bool:
        """
        Return truthiness based on the price value.

        PriceResult is falsy when price is 0, truthy otherwise.
        This enables existing `if price:` guards to work correctly.
        """
        return bool(self.price)

    def __float__(self) -> float:
        """
        Return the price as a float.

        This is needed for callers that do Decimal(float(result)).
        """
        return float(self.price)

    def __repr__(self) -> str:
        """
        Return a string representation showing price value and path summary.
        """
        path_summary = f"[{len(self.path)} steps]" if self.path else "[]"
        return f"PriceResult(price={self.price}, path={path_summary})"
