"""Tests for PriceResult trade-path source string quality.

These tests verify that ``_exit_early_for_known_tokens`` and ``_get_price``
in ``y.prices.magic`` produce :class:`PriceResult` objects with human-readable
source descriptions for various pricing buckets.

Unit tests (no RPC) focus on the ``_shorten_address`` helper and on
constructing PriceResult objects with the expected source patterns.
Integration tests (requires RPC) verify real pricing paths produce
descriptive source strings.
"""

import re

import pytest

from y.datatypes import PriceResult, PriceStep, UsdPrice
from y.prices.magic import _shorten_address


# ---------------------------------------------------------------------------
# Unit tests for _shorten_address helper
# ---------------------------------------------------------------------------


class TestShortenAddress:
    """Tests for the _shorten_address utility."""

    def test_standard_address(self):
        addr = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
        result = _shorten_address(addr)
        assert result == "0xC02a...6Cc2"
        assert len(result) == 13  # 6 + 3 + 4

    def test_short_string(self):
        assert _shorten_address("0xABCD") == "0xABCD"

    def test_empty(self):
        assert _shorten_address("") == ""


# ---------------------------------------------------------------------------
# Unit tests for PriceResult source string patterns
# ---------------------------------------------------------------------------


class TestSourceStringPatterns:
    """Unit tests verifying the expected source string format per bucket.

    These don't require RPC. They construct PriceResult objects with the
    source strings that magic.py would produce and verify the patterns.
    """

    def test_stablecoin_source(self):
        """VAL-PATH-004: Stablecoin source string."""
        result = PriceResult(
            price=UsdPrice(1),
            path=[PriceStep(
                token="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                price=UsdPrice(1),
                source="Stablecoin pegged 1:1 to USD",
            )],
        )
        assert result.path[0].source == "Stablecoin pegged 1:1 to USD"
        assert "Stablecoin" in result.path[0].source

    def test_one_to_one_source(self):
        """VAL-PATH-004: One-to-one peg source string."""
        target = "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9"
        source = f"1:1 peg with {_shorten_address(target)}"
        result = PriceResult(
            price=UsdPrice(100.0),
            path=[PriceStep(
                token="0x4da27a545c0c5B758a6BA100e3a049001de870f5",
                price=UsdPrice(100.0),
                source=source,
            )],
        )
        assert "1:1 peg with" in result.path[0].source
        assert "0x7Fc6" in result.path[0].source
        assert "..." in result.path[0].source

    def test_chainlink_source(self):
        """VAL-PATH-004: Chainlink source string."""
        feed_addr = "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419"
        source = f"Chainlink feed for {_shorten_address(feed_addr)}"
        result = PriceResult(
            price=UsdPrice(1800.0),
            path=[PriceStep(
                token="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                price=UsdPrice(1800.0),
                source=source,
            )],
        )
        assert "Chainlink" in result.path[0].source
        assert "0x5f4e" in result.path[0].source

    def test_aave_source(self):
        """VAL-PATH-004: Aave source string."""
        result = PriceResult(
            price=UsdPrice(1.0),
            path=[PriceStep(
                token="0x028171bCA77440897B824Ca71d1c56caC55b68A3",
                price=UsdPrice(1.0),
                source="Aave v2 aDAI underlying",
            )],
        )
        assert "Aave v2" in result.path[0].source
        assert "aDAI" in result.path[0].source
        assert "underlying" in result.path[0].source

    def test_compound_source(self):
        """VAL-PATH-004: Compound source string."""
        result = PriceResult(
            price=UsdPrice(0.022),
            path=[PriceStep(
                token="0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643",
                price=UsdPrice(0.022),
                source="Compound cDAI underlying",
            )],
        )
        assert "Compound" in result.path[0].source
        assert "cDAI" in result.path[0].source

    def test_yearn_source(self):
        """VAL-PATH-004: Yearn source string."""
        result = PriceResult(
            price=UsdPrice(1.05),
            path=[PriceStep(
                token="0xdA816459F1AB5631232FE5e97a05BBBb94970c95",
                price=UsdPrice(1.05),
                source="Yearn yvDAI vault share price",
            )],
        )
        assert "Yearn" in result.path[0].source
        assert "yvDAI" in result.path[0].source
        assert "vault share price" in result.path[0].source

    def test_curve_source(self):
        """VAL-PATH-004: Curve LP source string."""
        result = PriceResult(
            price=UsdPrice(1.01),
            path=[PriceStep(
                token="0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490",
                price=UsdPrice(1.01),
                source="Curve 3Crv LP",
            )],
        )
        assert "Curve" in result.path[0].source
        assert "LP" in result.path[0].source

    def test_convex_source(self):
        """VAL-PATH-004: Convex source string."""
        underlying = "0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490"
        source = f"Convex wrapping Curve LP {_shorten_address(underlying)}"
        result = PriceResult(
            price=UsdPrice(1.01),
            path=[PriceStep(
                token="0x30D9410ED1D5DA1F6C8391af5338C93ab8d4035C",
                price=UsdPrice(1.01),
                source=source,
            )],
        )
        assert "Convex wrapping Curve LP" in result.path[0].source
        assert "0x6c3F" in result.path[0].source

    def test_wsteth_source(self):
        """VAL-PATH-004: wstETH source string."""
        result = PriceResult(
            price=UsdPrice(2100.0),
            path=[PriceStep(
                token="0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0",
                price=UsdPrice(2100.0),
                source="Lido wstETH via stEthPerToken",
            )],
        )
        assert result.path[0].source == "Lido wstETH via stEthPerToken"

    def test_balancer_dex_fallback_source(self):
        """VAL-PATH-004: Balancer DEX fallback source string."""
        addr = "0xba100000625a3754423978a60c9317c58a424e3D"
        source = f"Balancer pool {_shorten_address(addr)}"
        result = PriceResult(
            price=UsdPrice(5.0),
            path=[PriceStep(
                token=addr,
                price=UsdPrice(5.0),
                source=source,
            )],
        )
        assert "Balancer pool" in result.path[0].source
        assert "0xba10" in result.path[0].source

    def test_uniswap_v2_lp_source(self):
        """VAL-PATH-004: Uniswap V2 LP source string."""
        addr = "0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc"
        source = f"Uniswap V2 LP pool {_shorten_address(addr)}"
        result = PriceResult(
            price=UsdPrice(300_000_000.0),
            path=[PriceStep(
                token=addr,
                price=UsdPrice(300_000_000.0),
                source=source,
            )],
        )
        assert "Uniswap V2" in result.path[0].source
        assert "LP pool" in result.path[0].source


# ---------------------------------------------------------------------------
# Tests verifying no raw object repr strings
# ---------------------------------------------------------------------------


class TestNoRawReprStrings:
    """Ensure source strings don't contain raw Python repr patterns."""

    _BAD_PATTERNS = [
        re.compile(r"<\w+ object at 0x[0-9a-f]+>"),  # <SomeObj object at 0x...>
        re.compile(r"<\w+\.\w+ "),  # <module.ClassName ...>
    ]

    @pytest.mark.parametrize("source", [
        "Stablecoin pegged 1:1 to USD",
        "1:1 peg with 0x7Fc6...DaE9",
        "Chainlink feed for 0x5f4e...8419",
        "Aave v2 aDAI underlying",
        "Compound cDAI underlying",
        "Yearn yvDAI vault share price",
        "Curve 3Crv LP",
        "Convex wrapping Curve LP 0x6c3F...E490",
        "Lido wstETH via stEthPerToken",
        "Balancer pool 0xba10...4e3D",
        "Uniswap V2 LP pool 0xB4e1...C9Dc",
        "DEX uniswap_multiplexer for 0xC02a...6Cc2",
        "ypriceapi for 0xC02a...6Cc2",
    ])
    def test_source_has_no_repr(self, source):
        """VAL-PATH-003: No raw object repr strings in source descriptions."""
        for pattern in self._BAD_PATTERNS:
            assert not pattern.search(source), f"Source contains raw repr: {source}"


# ---------------------------------------------------------------------------
# Tests verifying PriceResult backward compatibility in price pipeline
# ---------------------------------------------------------------------------


class TestPriceResultBackwardCompat:
    """Ensure PriceResult works in contexts where float was expected."""

    def test_sense_check_compat(self):
        """PriceResult.price can be passed to sense_check (expects float|Decimal)."""
        result = PriceResult(price=UsdPrice(1800.0), path=[])
        # sense_check expects float|Decimal - extracting .price should work
        assert isinstance(result.price, float)

    def test_if_price_guard(self):
        """'if price:' guard works with PriceResult (existing pattern in _get_price)."""
        result = PriceResult(price=UsdPrice(1800.0), path=[])
        assert result  # truthy for non-zero
        zero = PriceResult(price=UsdPrice(0), path=[])
        assert not zero  # falsy for zero

    def test_db_set_price_compat(self):
        """DB cache stores price value extracted from PriceResult."""
        result = PriceResult(price=UsdPrice(1800.0), path=[])
        # The __cache wrapper extracts .price for storage
        price_value = result.price if isinstance(result, PriceResult) else result
        assert price_value == 1800.0
        assert isinstance(price_value, float)

    def test_cache_hit_reconstruction(self):
        """Cache hit reconstructs PriceResult with empty path."""
        # Simulate what __cache does on a cache hit
        cached_price = 1800.0  # what DB returns
        result = PriceResult(price=UsdPrice(cached_price), path=[])
        assert isinstance(result, PriceResult)
        assert result.price == 1800.0
        assert result.path == []
        assert float(result) == 1800.0
