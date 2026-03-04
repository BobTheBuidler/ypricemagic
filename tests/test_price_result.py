"""
Unit tests for PriceResult and PriceStep dataclasses.

These tests verify the construction, truthiness, float conversion, and repr
behaviors of the new price result types.
"""

import pytest

from y import PriceResult, PriceStep
from y.datatypes import Price, UsdPrice


class TestPriceStep:
    """Tests for PriceStep dataclass."""

    def test_construction_all_fields(self) -> None:
        """PriceStep constructs correctly with all fields."""
        step = PriceStep(
            source="chainlink",
            input_token="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            output_token="USD",
            pool=None,
            price=1.5,
        )
        assert step.source == "chainlink"
        assert step.input_token == "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
        assert step.output_token == "USD"
        assert step.pool is None
        assert step.price == 1.5

    def test_construction_with_pool(self) -> None:
        """PriceStep constructs correctly with a pool address."""
        step = PriceStep(
            source="uniswap_v3",
            input_token="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            output_token="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            pool="0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640",
            price=2500.0,
        )
        assert step.pool == "0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640"

    def test_repr_shows_source_and_tokens(self) -> None:
        """repr shows source, input_token, and output_token."""
        step = PriceStep(
            source="chainlink",
            input_token="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            output_token="USD",
            pool=None,
            price=1.5,
        )
        result = repr(step)
        assert "chainlink" in result
        assert "input_token" in result
        assert "output_token" in result

    def test_repr_truncates_long_addresses(self) -> None:
        """repr truncates long token addresses for readability."""
        step = PriceStep(
            source="uniswap_v3",
            input_token="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            output_token="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            pool=None,
            price=2500.0,
        )
        result = repr(step)
        # Addresses should be truncated (first 6 + ... + last 4)
        assert "0xA0b8...eB48" in result
        assert "0xC02a...6Cc2" in result
        # Full addresses should NOT appear
        assert "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48" not in result

    def test_repr_includes_pool_when_present(self) -> None:
        """repr includes truncated pool address when present."""
        step = PriceStep(
            source="uniswap_v3",
            input_token="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            output_token="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            pool="0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640",
            price=2500.0,
        )
        result = repr(step)
        assert "pool=" in result
        assert "0x88e6...5640" in result


class TestPriceResult:
    """Tests for PriceResult dataclass."""

    def test_construction_with_usd_price(self) -> None:
        """PriceResult constructs correctly with UsdPrice."""
        result = PriceResult(price=UsdPrice(1234.56), path=[])
        assert result.price == 1234.56
        assert result.path == []

    def test_construction_with_float(self) -> None:
        """PriceResult constructs correctly with plain float."""
        result = PriceResult(price=1.5, path=[])
        assert result.price == 1.5

    def test_construction_with_path(self) -> None:
        """PriceResult constructs correctly with a path."""
        step = PriceStep(
            source="chainlink",
            input_token="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            output_token="USD",
            pool=None,
            price=1.0,
        )
        result = PriceResult(price=UsdPrice(1.0), path=[step])
        assert len(result.path) == 1
        assert result.path[0].source == "chainlink"

    def test_truthy_with_nonzero_price(self) -> None:
        """PriceResult with nonzero price is truthy."""
        result = PriceResult(price=UsdPrice(1.5), path=[])
        assert bool(result) is True

    def test_falsy_with_zero_price(self) -> None:
        """PriceResult with zero price is falsy."""
        result = PriceResult(price=UsdPrice(0), path=[])
        assert bool(result) is False

    def test_falsy_with_zero_price_and_path(self) -> None:
        """PriceResult with zero price is falsy even with a path."""
        step = PriceStep(
            source="dex",
            input_token="0xToken",
            output_token="0xQuote",
            pool="0xPool",
            price=0.0,
        )
        result = PriceResult(price=UsdPrice(0), path=[step])
        assert bool(result) is False

    def test_float_conversion(self) -> None:
        """float(PriceResult) returns float(price)."""
        result = PriceResult(price=UsdPrice(1234.56), path=[])
        assert float(result) == 1234.56

    def test_float_conversion_with_price_type(self) -> None:
        """float(PriceResult) works with Price type."""
        result = PriceResult(price=Price(0.0005), path=[])
        assert float(result) == 0.0005

    def test_repr_shows_price_and_path_summary(self) -> None:
        """repr shows price value and path summary."""
        result = PriceResult(price=UsdPrice(1234.56), path=[])
        repr_str = repr(result)
        assert "1234.56" in repr_str
        assert "path=[]" in repr_str

    def test_repr_shows_step_count_for_nonempty_path(self) -> None:
        """repr shows step count for non-empty path."""
        step = PriceStep(
            source="chainlink",
            input_token="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            output_token="USD",
            pool=None,
            price=1.0,
        )
        result = PriceResult(price=UsdPrice(1.0), path=[step])
        repr_str = repr(result)
        assert "1 steps" in repr_str or "[1 steps]" in repr_str

    def test_multiple_steps_in_path(self) -> None:
        """PriceResult can have multiple steps in path."""
        step1 = PriceStep(
            source="atoken",
            input_token="0xAToken",
            output_token="0xUnderlying",
            pool=None,
            price=1.0,
        )
        step2 = PriceStep(
            source="chainlink",
            input_token="0xUnderlying",
            output_token="USD",
            pool=None,
            price=2500.0,
        )
        result = PriceResult(price=UsdPrice(2500.0), path=[step1, step2])
        assert len(result.path) == 2
        assert result.path[0].source == "atoken"
        assert result.path[1].source == "chainlink"


class TestImports:
    """Tests for import paths."""

    def test_import_from_y_datatypes(self) -> None:
        """PriceResult and PriceStep can be imported from y.datatypes."""
        from y.datatypes import PriceResult, PriceStep

        assert PriceResult is not None
        assert PriceStep is not None

    def test_import_from_y(self) -> None:
        """PriceResult and PriceStep can be imported from y."""
        from y import PriceResult, PriceStep

        assert PriceResult is not None
        assert PriceStep is not None
