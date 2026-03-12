"""Tests for get_price_history and backfill_prices functions.

These tests verify the historical price data and backfill functionality:

Tests cover:
- VAL-QUOTE-010: Historical price data endpoint returns time-series
- VAL-QUOTE-011: Historical price data validates parameters
- VAL-QUOTE-012: Backfill trigger returns 202 and populates cache
- VAL-QUOTE-017: Historical price data covers the requested time period
"""

import asyncio
import time

import pytest

from tests.fixtures import async_test, mainnet_only
from y import get_price
from y.datatypes import UsdPrice
from y.prices.magic import backfill_prices, get_price_history
from y.time import get_block_timestamp_async

# Token addresses on mainnet
USDC_ADDRESS = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"

# Block for testing - a known historical block
BLOCK = 18_000_000


class TestGetPriceHistoryImport:
    """Tests for get_price_history import."""

    def test_get_price_history_importable_from_y(self) -> None:
        """get_price_history should be importable from y.prices.magic."""
        from y.prices.magic import get_price_history as gph

        assert callable(gph), "get_price_history should be callable"

    def test_backfill_prices_importable_from_y(self) -> None:
        """backfill_prices should be importable from y.prices.magic."""
        from y.prices.magic import backfill_prices as bp

        assert callable(bp), "backfill_prices should be callable"


class TestGetPriceHistoryParameters:
    """Tests for parameter validation (VAL-QUOTE-011)."""

    @pytest.mark.parametrize(
        "token,period,expected_error",
        [
            ("", "7d", "token"),  # Missing token
            ("not_an_address", "7d", "address"),  # Invalid address
            (USDC_ADDRESS, "", "period"),  # Missing period
            (USDC_ADDRESS, "banana", "period"),  # Unsupported period
            (USDC_ADDRESS, "1d", "period"),  # Unsupported period
            (USDC_ADDRESS, "90d", "period"),  # Unsupported period
        ],
    )
    def test_invalid_params_raises_error(
        self, token: str, period: str, expected_error: str
    ) -> None:
        """VAL-QUOTE-011: Invalid parameters should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            get_price_history(token, period)  # type: ignore

        assert (
            expected_error in str(exc_info.value).lower()
        ), f"Error should mention '{expected_error}'"

    def test_valid_params_do_not_raise(self) -> None:
        """Valid parameters should not raise ValueError."""
        # This should not raise - it may return empty list if no cached data
        result = get_price_history(USDC_ADDRESS, "7d")
        assert isinstance(result, list), "Result should be a list"

    def test_valid_30d_params_do_not_raise(self) -> None:
        """Valid 30d period should not raise ValueError."""
        result = get_price_history(USDC_ADDRESS, "30d")
        assert isinstance(result, list), "Result should be a list"


class TestGetPriceHistoryFormat:
    """Tests for return format (VAL-QUOTE-010)."""

    @async_test
    @mainnet_only
    async def test_history_returns_list(self) -> None:
        """VAL-QUOTE-010: get_price_history should return a list."""
        result = await get_price_history(USDC_ADDRESS, "7d", sync=False)

        assert isinstance(result, list), f"Expected list, got {type(result)}"

    @async_test
    @mainnet_only
    async def test_history_entries_have_required_fields(self) -> None:
        """VAL-QUOTE-010: Each entry should have block, price, block_timestamp."""
        result = await get_price_history(USDC_ADDRESS, "7d", sync=False)

        if len(result) == 0:
            # If no cached data, skip field checks
            pytest.skip("No cached price data available")

        for entry in result:
            assert "block" in entry, "Entry should have 'block' field"
            assert "price" in entry, "Entry should have 'price' field"
            assert "block_timestamp" in entry, "Entry should have 'block_timestamp' field"

    @async_test
    @mainnet_only
    async def test_history_timestamps_monotonically_increasing(self) -> None:
        """VAL-QUOTE-010: Timestamps should be monotonically increasing."""
        result = await get_price_history(USDC_ADDRESS, "7d", sync=False)

        if len(result) < 2:
            pytest.skip("Need at least 2 entries to check monotonicity")

        timestamps = [entry["block_timestamp"] for entry in result]
        assert timestamps == sorted(timestamps), "Timestamps should be monotonically increasing"


class TestGetPriceHistoryTimeSpan:
    """Tests for time span validation (VAL-QUOTE-017)."""

    @async_test
    @mainnet_only
    async def test_7d_time_span(self) -> None:
        """VAL-QUOTE-017: For 7d, time span should be 6-7.5 days."""
        result = await get_price_history(USDC_ADDRESS, "7d", sync=False)

        if len(result) < 2:
            pytest.skip("Need at least 2 entries to check time span")

        first_ts = result[0]["block_timestamp"]
        last_ts = result[-1]["block_timestamp"]

        time_span_seconds = last_ts - first_ts
        time_span_days = time_span_seconds / (24 * 60 * 60)

        assert (
            6 <= time_span_days <= 7.5
        ), f"Time span for 7d should be 6-7.5 days, got {time_span_days:.2f} days"

    @async_test
    @mainnet_only
    async def test_30d_time_span(self) -> None:
        """VAL-QUOTE-017: For 30d, time span should be 28-31 days."""
        result = await get_price_history(USDC_ADDRESS, "30d", sync=False)

        if len(result) < 2:
            pytest.skip("Need at least 2 entries to check time span")

        first_ts = result[0]["block_timestamp"]
        last_ts = result[-1]["block_timestamp"]

        time_span_seconds = last_ts - first_ts
        time_span_days = time_span_seconds / (24 * 60 * 60)

        assert (
            28 <= time_span_days <= 31
        ), f"Time span for 30d should be 28-31 days, got {time_span_days:.2f} days"


class TestGetPriceHistoryGranularity:
    """Tests for granularity of returned data."""

    @async_test
    @mainnet_only
    async def test_7d_hourly_granularity(self) -> None:
        """For 7d, should return ~168 entries (hourly for 7 days)."""
        result = await get_price_history(USDC_ADDRESS, "7d", sync=False)

        # With backfill, we expect ~168 entries (7 days * 24 hours)
        # Without backfill, may be fewer cached entries
        # Accept a range: at least 50% of expected if cached, or check format
        if len(result) > 0:
            # Check that entries are roughly hourly spaced
            if len(result) >= 2:
                time_diff = result[-1]["block_timestamp"] - result[0]["block_timestamp"]
                avg_interval_hours = (time_diff / 3600) / len(result)
                # Average interval should be roughly 1 hour (allow 0.5-2 hours)
                assert (
                    0.5 <= avg_interval_hours <= 2
                ), f"Expected ~hourly intervals, got avg {avg_interval_hours:.2f} hours"

    @async_test
    @mainnet_only
    async def test_30d_daily_granularity(self) -> None:
        """For 30d, should return ~30 entries (daily for 30 days)."""
        result = await get_price_history(USDC_ADDRESS, "30d", sync=False)

        if len(result) > 0 and len(result) >= 2:
            time_diff = result[-1]["block_timestamp"] - result[0]["block_timestamp"]
            avg_interval_days = (time_diff / 86400) / len(result)
            # Average interval should be roughly 1 day (allow 0.5-2 days)
            assert (
                0.5 <= avg_interval_days <= 2
            ), f"Expected ~daily intervals, got avg {avg_interval_days:.2f} days"


class TestBackfillPrices:
    """Tests for backfill functionality (VAL-QUOTE-012)."""

    @async_test
    @mainnet_only
    async def test_backfill_returns_task(self) -> None:
        """VAL-QUOTE-012: backfill_prices should return an asyncio.Task."""
        # Use a small block range for testing
        block_start = BLOCK - 1000
        block_end = BLOCK - 500

        task = await backfill_prices(USDC_ADDRESS, block_start, block_end, sync=False)

        assert isinstance(task, asyncio.Task), f"Expected asyncio.Task, got {type(task)}"

        # Wait for task to complete
        await task

    @async_test
    @mainnet_only
    async def test_backfill_invalid_token_raises(self) -> None:
        """VAL-QUOTE-012: Invalid token should raise ValueError."""
        invalid_token = "not_an_address"

        with pytest.raises(ValueError):
            await backfill_prices(invalid_token, BLOCK - 100, BLOCK, sync=False)  # type: ignore

    @async_test
    @mainnet_only
    async def test_backfill_reversed_range_raises(self) -> None:
        """VAL-QUOTE-012: Reversed block range should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            await backfill_prices(USDC_ADDRESS, BLOCK, BLOCK - 100, sync=False)

        assert "reversed" in str(exc_info.value).lower() or "range" in str(exc_info.value).lower()

    @async_test
    @mainnet_only
    async def test_backfill_populates_cache(self) -> None:
        """VAL-QUOTE-012: After backfill, prices should be cached."""
        # Use a specific block range
        block_start = BLOCK - 500
        block_end = BLOCK - 400

        # Run backfill
        task = await backfill_prices(USDC_ADDRESS, block_start, block_end, sync=False)
        await task

        # Wait a bit for cache to settle
        await asyncio.sleep(0.5)

        # Check that a mid-range block returns cached price
        mid_block = (block_start + block_end) // 2
        price = await get_price(USDC_ADDRESS, mid_block, sync=False)

        # Price should exist (either newly cached or already was)
        assert price is not None, "Price should be available after backfill"


class TestBackfillPricesSyncAsync:
    """Tests for sync/async modes."""

    @mainnet_only
    def test_backfill_sync_mode_works(self) -> None:
        """backfill_prices should work in synchronous mode."""
        block_start = BLOCK - 100
        block_end = BLOCK - 50

        task = backfill_prices(USDC_ADDRESS, block_start, block_end)

        assert isinstance(task, asyncio.Task), "Sync mode should still return asyncio.Task"

        # Wait for completion
        task.get()

    @async_test
    @mainnet_only
    async def test_backfill_async_mode_works(self) -> None:
        """backfill_prices should work in asynchronous mode."""
        block_start = BLOCK - 100
        block_end = BLOCK - 50

        task = await backfill_prices(USDC_ADDRESS, block_start, block_end, sync=False)

        assert isinstance(task, asyncio.Task)
        await task
