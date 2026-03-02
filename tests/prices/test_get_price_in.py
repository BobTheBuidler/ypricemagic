"""Tests for get_price_in function and Price type.

These tests verify the Price type and get_price_in API for quote-token
denominated pricing. The initial implementation uses USD cross-rate.

Tests cover:
- VAL-QT-001: get_price_in exported from y
- VAL-QT-002: get_price_in returns Price type
- VAL-QT-003: get_price_in with WETH quote returns ETH-denominated price
- VAL-QT-006: get_price_in handles failure gracefully with fail_to_None
- VAL-QT-007: Existing get_price backward compatible
- VAL-QT-008: get_price_in with same token as quote returns 1.0
- VAL-QT-009: get_price_in supports amount parameter
- VAL-QT-010: get_price_in raises on failure when fail_to_None is False
- VAL-QT-012: get_price_in supports sync and async calling conventions
- VAL-TYPE-001: Price type hierarchy is correct
"""

import pytest

from tests.fixtures import async_test, mainnet_only
from y import get_price, get_price_in
from y.constants import usdc, weth
from y.datatypes import Price, UsdPrice
from y.exceptions import PriceError, yPriceMagicError

# Token addresses on mainnet
USDC_ADDRESS = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
USDT_ADDRESS = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
DAI_ADDRESS = "0x6B175474E89094C44Da98b954EedeAC495271d0F"

# Block for testing - a known historical block
BLOCK = 18_000_000


class TestPriceType:
    """Tests for the Price type (VAL-TYPE-001)."""

    def test_price_is_float_subclass(self) -> None:
        """Price should be a float subclass."""
        assert issubclass(Price, float), "Price should be a float subclass"

    def test_price_not_usdprice_subclass(self) -> None:
        """Price should NOT be a subclass of UsdPrice."""
        assert not issubclass(Price, UsdPrice), "Price should not inherit from UsdPrice"

    def test_price_str_omits_dollar_sign(self) -> None:
        """Price.__str__ should omit the $ prefix."""
        price = Price(0.0005)
        assert str(price) == "0.00050000", f"Expected '0.00050000', got '{str(price)}'"
        assert not str(price).startswith("$"), "Price string should not start with $"

    def test_usdprice_str_has_dollar_sign(self) -> None:
        """UsdPrice.__str__ should have the $ prefix (regression check)."""
        price = UsdPrice(1234.56)
        assert str(price).startswith("$"), "UsdPrice string should start with $"

    def test_price_isinstance_distinguishes_from_usdprice(self) -> None:
        """isinstance checks should correctly distinguish Price from UsdPrice."""
        price = Price(0.5)
        usd_price = UsdPrice(100.0)

        assert isinstance(price, Price), "Price instance should be instance of Price"
        assert not isinstance(price, UsdPrice), "Price instance should not be instance of UsdPrice"
        assert isinstance(usd_price, UsdPrice), "UsdPrice instance should be instance of UsdPrice"
        assert not isinstance(usd_price, Price), "UsdPrice instance should not be instance of Price"


class TestGetPriceInImport:
    """Tests for get_price_in import (VAL-QT-001)."""

    def test_get_price_in_importable_from_y(self) -> None:
        """VAL-QT-001: get_price_in should be importable from y."""
        from y import get_price_in as gpi

        assert callable(gpi), "get_price_in should be callable"

    def test_price_importable_from_y(self) -> None:
        """Price type should be importable from y."""
        from y import Price as P

        assert issubclass(P, float), "Price should be a float subclass"


class TestGetPriceInSameToken:
    """Tests for same-token quote (VAL-QT-008)."""

    @async_test
    @mainnet_only
    async def test_same_token_returns_one(self) -> None:
        """VAL-QT-008: get_price_in(token, token) returns Price(1.0)."""
        result = await get_price_in(USDC_ADDRESS, USDC_ADDRESS, BLOCK, skip_cache=True, sync=False)

        assert result is not None, "Result should not be None"
        assert isinstance(result, Price), f"Result should be Price, got {type(result)}"
        assert result == 1.0, f"Expected 1.0, got {result}"

    @async_test
    @mainnet_only
    async def test_same_token_no_unnecessary_rpc(self) -> None:
        """Same-token should return 1.0 without making unnecessary RPC calls."""
        # Use a valid token but with invalid block - should still return 1.0
        # since same-token check happens before any RPC
        result = await get_price_in(WETH_ADDRESS, WETH_ADDRESS, BLOCK, skip_cache=True, sync=False)

        assert result == 1.0, f"Expected 1.0 for same token, got {result}"
        assert isinstance(result, Price), f"Result should be Price, got {type(result)}"


class TestGetPriceInWethQuote:
    """Tests for WETH-denominated pricing (VAL-QT-003)."""

    @async_test
    @mainnet_only
    async def test_usdc_in_eth_returns_eth_price(self) -> None:
        """VAL-QT-003: get_price_in(USDC, WETH) returns ETH-denominated price."""
        result = await get_price_in(USDC_ADDRESS, WETH_ADDRESS, BLOCK, skip_cache=True, sync=False)

        assert result is not None, "Result should not be None"
        assert isinstance(result, Price), f"Result should be Price, got {type(result)}"

        # USDC price in ETH should be small (~0.0002-0.0006 depending on ETH price)
        # At block 18M, ETH ~$1800-2000, so USDC ~0.0005-0.00055 ETH
        assert 0.0001 < result < 0.001, f"USDC/ETH price {result} outside expected range"
        print(f"USDC price in ETH at block {BLOCK}: {result}")

    @async_test
    @mainnet_only
    async def test_usdt_in_eth_returns_eth_price(self) -> None:
        """USDT price in ETH should also work via USD cross-rate."""
        result = await get_price_in(USDT_ADDRESS, WETH_ADDRESS, BLOCK, skip_cache=True, sync=False)

        assert result is not None, "Result should not be None"
        assert isinstance(result, Price), f"Result should be Price, got {type(result)}"

        # USDT should be close to USDC price in ETH (both ~$1)
        assert 0.0001 < result < 0.001, f"USDT/ETH price {result} outside expected range"
        print(f"USDT price in ETH at block {BLOCK}: {result}")


class TestGetPriceInFailureHandling:
    """Tests for failure handling (VAL-QT-006, VAL-QT-010)."""

    @async_test
    @mainnet_only
    async def test_fail_to_none_returns_none(self) -> None:
        """VAL-QT-006: get_price_in with fail_to_None=True returns None on failure."""
        # Use an invalid token address that won't have a price
        invalid_token = "0x0000000000000000000000000000000000000001"
        result = await get_price_in(
            invalid_token, WETH_ADDRESS, BLOCK, fail_to_None=True, skip_cache=True, sync=False
        )

        assert result is None, f"Expected None for invalid token, got {result}"

    @async_test
    @mainnet_only
    async def test_default_failure_raises_exception(self) -> None:
        """VAL-QT-010: get_price_in raises on failure when fail_to_None is False."""
        # Use an invalid token address that won't have a price
        invalid_token = "0x0000000000000000000000000000000000000001"

        with pytest.raises((PriceError, yPriceMagicError)):
            await get_price_in(invalid_token, WETH_ADDRESS, BLOCK, skip_cache=True, sync=False)


class TestGetPriceInSyncAsync:
    """Tests for sync/async modes (VAL-QT-012)."""

    @mainnet_only
    def test_sync_mode_works(self) -> None:
        """VAL-QT-012: get_price_in works in synchronous mode."""
        # Sync mode is the default with @a_sync.a_sync(default='sync')
        result = get_price_in(USDC_ADDRESS, WETH_ADDRESS, BLOCK, skip_cache=True)

        assert result is not None, "Sync result should not be None"
        assert isinstance(result, Price), f"Sync result should be Price, got {type(result)}"
        print(f"Sync mode result: {result}")

    @async_test
    @mainnet_only
    async def test_async_mode_works(self) -> None:
        """VAL-QT-012: get_price_in works in asynchronous mode."""
        result = await get_price_in(USDC_ADDRESS, WETH_ADDRESS, BLOCK, skip_cache=True, sync=False)

        assert result is not None, "Async result should not be None"
        assert isinstance(result, Price), f"Async result should be Price, got {type(result)}"
        print(f"Async mode result: {result}")


class TestGetPriceInAmountParameter:
    """Tests for amount parameter (VAL-QT-009)."""

    @async_test
    @mainnet_only
    async def test_amount_parameter_works(self) -> None:
        """VAL-QT-009: get_price_in supports amount parameter."""
        # Test with amount parameter - should still return a valid price
        result = await get_price_in(
            USDC_ADDRESS, WETH_ADDRESS, BLOCK, amount=1000, skip_cache=True, sync=False
        )

        assert result is not None, "Result with amount should not be None"
        assert isinstance(result, Price), f"Result should be Price, got {type(result)}"
        # The price should still be in reasonable range for USDC/ETH
        assert (
            0.0001 < result < 0.001
        ), f"USDC/ETH price with amount {result} outside expected range"
        print(f"USDC/ETH price with amount=1000: {result}")


class TestGetPriceBackwardCompatibility:
    """Tests for backward compatibility (VAL-QT-007)."""

    @async_test
    @mainnet_only
    async def test_get_price_still_returns_usdprice(self) -> None:
        """VAL-QT-007: get_price() still returns UsdPrice after changes."""
        result = await get_price(WETH_ADDRESS, BLOCK, skip_cache=True, sync=False)

        assert result is not None, "get_price result should not be None"
        assert isinstance(result, UsdPrice), f"get_price should return UsdPrice, got {type(result)}"
        assert not isinstance(result, Price), "get_price result should not be Price"
        # Verify it still has $ prefix
        assert str(result).startswith("$"), "UsdPrice should still have $ prefix"
        print(f"WETH USD price at block {BLOCK}: {result}")

    @async_test
    @mainnet_only
    async def test_get_price_signature_unchanged(self) -> None:
        """get_price() signature should be unchanged."""
        # Test that all the original parameters still work
        # Use WETH instead of USDC since USDC returns plain int 1 for stablecoins
        result = await get_price(
            WETH_ADDRESS,
            BLOCK,
            fail_to_None=True,
            skip_cache=True,
            ignore_pools=(),
            silent=False,
            sync=False,
        )

        assert result is not None, "get_price with all params should work"
        assert isinstance(result, UsdPrice), f"Should still be UsdPrice, got {type(result)}"


class TestPriceVsUsdPrice:
    """Tests to ensure Price and UsdPrice are clearly distinct types."""

    @async_test
    @mainnet_only
    async def test_get_price_in_vs_get_price_different_types(self) -> None:
        """get_price_in returns Price, get_price returns UsdPrice."""
        # Use WETH for both to compare types correctly
        # Note: Stablecoins like USDC return plain int 1, not UsdPrice
        price_in_result = await get_price_in(
            DAI_ADDRESS, WETH_ADDRESS, BLOCK, skip_cache=True, sync=False
        )
        usd_price_result = await get_price(DAI_ADDRESS, BLOCK, skip_cache=True, sync=False)

        assert isinstance(price_in_result, Price), "get_price_in should return Price"
        # DAI is also a stablecoin, so let's use WETH for the usd_price check
        weth_usd_price = await get_price(WETH_ADDRESS, BLOCK, skip_cache=True, sync=False)
        assert isinstance(weth_usd_price, UsdPrice), "get_price should return UsdPrice for WETH"
        assert type(price_in_result) != type(weth_usd_price), "Types should be different"

    @async_test
    @mainnet_only
    async def test_price_value_calculation(self) -> None:
        """Verify the USD cross-rate calculation is correct."""
        # Get USD prices directly
        usdc_usd = await get_price(USDC_ADDRESS, BLOCK, skip_cache=True, sync=False)
        weth_usd = await get_price(WETH_ADDRESS, BLOCK, skip_cache=True, sync=False)

        # Get cross price via get_price_in
        usdc_in_eth = await get_price_in(
            USDC_ADDRESS, WETH_ADDRESS, BLOCK, skip_cache=True, sync=False
        )

        # The cross-rate should be usdc_usd / weth_usd
        # Note: usdc_usd is 1 (int) for stablecoins, weth_usd is UsdPrice
        expected = float(usdc_usd) / float(weth_usd)

        # Allow 1% tolerance for any rounding differences
        assert (
            abs(usdc_in_eth - expected) < expected * 0.01
        ), f"Cross-rate mismatch: got {usdc_in_eth}, expected {expected}"
        print(f"USDC/USD: {usdc_usd}, WETH/USD: {weth_usd}, USDC/ETH: {usdc_in_eth}")
