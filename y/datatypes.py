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
    """Represents a single step in a price derivation path.

    Each step captures how a price was derived at a particular stage of
    resolution, including the token involved, the intermediate price, and a
    human-readable description of the pricing source.

    Attributes:
        token: The token address for this step.
        price: The price at this step (typically :class:`UsdPrice`).
        source: Human-readable description of the pricing source
            (e.g. ``"Chainlink ETH/USD feed 0x5f4e..."``).

    Examples:
        >>> step = PriceStep(
        ...     token='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        ...     price=UsdPrice(1800.0),
        ...     source='Chainlink ETH/USD feed 0x5f4e...',
        ... )
        >>> step.source
        'Chainlink ETH/USD feed 0x5f4e...'
    """

    token: str
    price: UsdPrice
    source: str

    def __repr__(self) -> str:
        """Return a concise string representation of the price step."""
        # Truncate long addresses for readability
        tok = (
            self.token[:6] + "..." + self.token[-4:]
            if len(self.token) > 12
            else self.token
        )
        return (
            f"PriceStep(token='{tok}', price={self.price}, source='{self.source}')"
        )


@dataclass(eq=False)
class PriceResult:
    """Result of a price resolution with derivation path information.

    Wraps the final price together with the list of :class:`PriceStep` objects
    that describe *how* the price was derived.  This enables callers to
    inspect the full derivation chain for audit / debugging.

    **Backward-compatible with float:** existing code that treats the return
    value as a number (``float(result)``, ``result > 0``, ``result * 2``)
    continues to work.  ``Decimal(result.price)`` works; ``Decimal(result)``
    intentionally raises ``TypeError`` so callers extract ``.price`` first.

    Attributes:
        price: The final USD price (typically :class:`UsdPrice`).
        path: List of :class:`PriceStep` objects showing the derivation path.

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

    price: UsdPrice
    path: list[PriceStep]

    # ------------------------------------------------------------------
    # float backward-compatibility
    # ------------------------------------------------------------------

    def __float__(self) -> float:
        """Return the price as a plain float.

        Enables ``Decimal(float(result))`` and any API expecting a float.
        """
        return float(self.price)

    def __bool__(self) -> bool:
        """Truthiness based on the price value.

        ``PriceResult`` is falsy when ``price`` is ``0``, truthy otherwise.
        This keeps existing ``if price:`` guards working.
        """
        return bool(self.price)

    # ------------------------------------------------------------------
    # comparison operators
    # ------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        """Compare with another :class:`PriceResult` or a numeric value.

        When comparing two ``PriceResult`` instances, both ``price`` **and**
        ``path`` must match.  When comparing with a numeric type, only
        ``price`` is considered.
        """
        if isinstance(other, PriceResult):
            return self.price == other.price and self.path == other.path
        try:
            return float(self) == float(other)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return NotImplemented  # type: ignore[return-value]

    def __hash__(self) -> int:
        """Hash based on price value (path is mutable, so not included)."""
        return hash(float(self))

    def __gt__(self, other: object) -> bool:
        return float(self) > float(other)  # type: ignore[arg-type]

    def __lt__(self, other: object) -> bool:
        return float(self) < float(other)  # type: ignore[arg-type]

    def __ge__(self, other: object) -> bool:
        return float(self) >= float(other)  # type: ignore[arg-type]

    def __le__(self, other: object) -> bool:
        return float(self) <= float(other)  # type: ignore[arg-type]

    # ------------------------------------------------------------------
    # arithmetic operators
    # ------------------------------------------------------------------

    def __mul__(self, other: object) -> float:
        return float(self) * float(other)  # type: ignore[arg-type]

    def __rmul__(self, other: object) -> float:
        return float(other) * float(self)  # type: ignore[arg-type]

    def __truediv__(self, other: object) -> float:
        return float(self) / float(other)  # type: ignore[arg-type]

    def __rtruediv__(self, other: object) -> float:
        return float(other) / float(self)  # type: ignore[arg-type]

    def __add__(self, other: object) -> float:
        return float(self) + float(other)  # type: ignore[arg-type]

    def __radd__(self, other: object) -> float:
        return float(other) + float(self)  # type: ignore[arg-type]

    def __sub__(self, other: object) -> float:
        return float(self) - float(other)  # type: ignore[arg-type]

    def __rsub__(self, other: object) -> float:
        return float(other) - float(self)  # type: ignore[arg-type]

    def __abs__(self) -> float:
        return abs(float(self))

    # ------------------------------------------------------------------
    # string representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        path_summary = f"[{len(self.path)} steps]" if self.path else "[]"
        return f"PriceResult(price={self.price}, path={path_summary})"
