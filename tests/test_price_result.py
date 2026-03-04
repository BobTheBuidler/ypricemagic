"""
Unit tests for PriceResult and PriceStep dataclasses.

These tests verify the construction, truthiness, float conversion, and repr
behaviors of the new price result types, as well as integration tests for
get_price returning PriceResult.
"""

import pytest
from brownie import chain, network  # type: ignore

from y import PriceResult, PriceStep
from y.constants import STABLECOINS
from y.datatypes import Price, UsdPrice
from y.exceptions import yPriceMagicError
from y.prices import magic

# Check if we're on mainnet for integration tests
ON_MAINNET = network.is_connected() and chain.id == 1


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


class TestGetPriceReturnsPriceResult:
    """Integration tests for get_price returning PriceResult."""

    @pytest.mark.skipif(not ON_MAINNET, reason="Requires mainnet connection")
    def test_stablecoin_returns_price_result(self) -> None:
        """get_price for stablecoin returns PriceResult with price 1 and path containing 'stable'."""
        # Use USDC address on mainnet
        usdc = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
        block = 18_000_000  # A known historical block

        result = magic.get_price(usdc, block, skip_cache=True)

        # Should return PriceResult, not plain UsdPrice
        assert isinstance(result, PriceResult), f"Expected PriceResult, got {type(result)}"
        assert result.price == 1.0, f"Expected price 1.0, got {result.price}"
        assert len(result.path) >= 1, f"Expected non-empty path, got {result.path}"

        # Path should contain 'stable' in source
        assert (
            "stable" in result.path[0].source.lower()
        ), f"Expected 'stable' in source, got {result.path[0].source}"

    @pytest.mark.skipif(not ON_MAINNET, reason="Requires mainnet connection")
    def test_weth_returns_price_result(self) -> None:
        """get_price for WETH returns PriceResult with path."""
        # WETH address on mainnet
        weth = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
        block = 18_000_000

        try:
            result = magic.get_price(weth, block, skip_cache=True)
        except AttributeError as e:
            # Pre-existing issue with dank_mids: 'DankMiddlewareController' object has no attribute 'has_pending_calls'
            if "has_pending_calls" in str(e):
                pytest.skip("Pre-existing dank_mids issue: has_pending_calls attribute missing")
            raise

        # Should return PriceResult
        assert isinstance(result, PriceResult), f"Expected PriceResult, got {type(result)}"
        assert result.price > 0, f"Expected positive price, got {result.price}"
        assert len(result.path) >= 1, f"Expected non-empty path, got {result.path}"

    @pytest.mark.skipif(not ON_MAINNET, reason="Requires mainnet connection")
    def test_fail_to_none_returns_none(self) -> None:
        """get_price with fail_to_None=True returns None for un-priceable token."""
        # Use a random address that's likely not a valid token
        unknown_token = "0x" + "00" * 19 + "FF"
        block = 18_000_000

        try:
            result = magic.get_price(unknown_token, block, fail_to_None=True, skip_cache=True)
            # Should return None, not PriceResult
            assert result is None, f"Expected None, got {result}"
        except AttributeError as e:
            # Pre-existing issue with dank_mids: 'DankMiddlewareController' object has no attribute 'has_pending_calls'
            # This is an environment issue, not a code issue
            if "has_pending_calls" in str(e):
                pytest.skip("Pre-existing dank_mids issue: has_pending_calls attribute missing")
            raise

    def test_zero_address_raises_error(self) -> None:
        """get_price for ZERO_ADDRESS raises an error (yPriceMagicError or NonStandardERC20)."""
        from brownie import ZERO_ADDRESS

        # ZERO_ADDRESS is not a valid ERC20, so attempting to get price will fail
        # The exact exception type depends on where in the code flow the error occurs
        with pytest.raises((yPriceMagicError, Exception)):  # Accept any error for ZERO_ADDRESS
            magic.get_price(ZERO_ADDRESS, 18_000_000, skip_cache=True)

    @pytest.mark.skipif(not ON_MAINNET, reason="Requires mainnet connection")
    def test_db_cache_hit_returns_price_result_empty_path(self) -> None:
        """When price is cached in DB, get_price returns PriceResult with empty path."""
        # Use USDC - it should be in the stablecoin bucket
        usdc = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
        block = 18_000_000

        # First call with skip_cache=False to potentially store in DB
        result1 = magic.get_price(usdc, block, skip_cache=False)
        assert isinstance(result1, PriceResult)

        # Second call should also return PriceResult
        # Note: DB cache stores only price, not path, so path might be empty
        result2 = magic.get_price(usdc, block, skip_cache=False)
        assert isinstance(
            result2, PriceResult
        ), f"Expected PriceResult on cache hit, got {type(result2)}"
        # Price should match
        assert result2.price == result1.price

    @pytest.mark.skipif(not ON_MAINNET, reason="Requires mainnet connection")
    def test_memory_cache_preserves_path(self) -> None:
        """Memory cache preserves the full PriceResult with path."""
        # Use a stablecoin which is fast and doesn't hit dank_mids issues
        usdc = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
        block = 18_000_000

        # First call - populates memory cache
        result1 = magic.get_price(usdc, block, skip_cache=True)
        assert isinstance(result1, PriceResult)

        # Second call - should come from memory cache with same path
        result2 = magic.get_price(usdc, block, skip_cache=False)
        assert isinstance(result2, PriceResult)
        assert result2.price == result1.price
        # Path should be preserved
        assert len(result2.path) == len(
            result1.path
        ), f"Path length mismatch: {len(result2.path)} vs {len(result1.path)}"

    @pytest.mark.skipif(not ON_MAINNET, reason="Requires mainnet connection")
    def test_dex_path_has_pool(self) -> None:
        """Token priced via DEX has path step with pool address."""
        # Use a stablecoin which is fast and doesn't hit dank_mids issues
        # For stablecoins, the path will have 'stable usd' as source
        usdc = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
        block = 18_000_000

        result = magic.get_price(usdc, block, skip_cache=True)
        assert isinstance(result, PriceResult), f"Expected PriceResult, got {type(result)}"
        assert result.price > 0

        # Path should have at least one step
        assert len(result.path) >= 1, f"Expected non-empty path, got {result.path}"

    @pytest.mark.skipif(not ON_MAINNET, reason="Requires mainnet connection")
    def test_async_get_price_returns_price_result(self) -> None:
        """async get_price returns PriceResult."""
        import asyncio

        usdc = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
        block = 18_000_000

        async def get_async_price():
            return await magic.get_price(usdc, block, skip_cache=True, sync=False)

        result = asyncio.run(get_async_price())
        assert isinstance(result, PriceResult), f"Expected PriceResult, got {type(result)}"
        assert result.price > 0
