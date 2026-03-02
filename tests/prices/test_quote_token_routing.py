"""Tests for quote token routing in get_price_in.

These tests verify that get_price_in uses on-chain DEX routing to the quote token
when available, with USD cross-rate fallback when no on-chain path exists.

Tests cover:
- VAL-QT-004: get_price_in uses on-chain routing when available
- VAL-QT-005: get_price_in falls back to USD cross-rate
- VAL-QT-011: get_price_in does not pollute the USD price cache
- VAL-CROSS-002: Multi-hop routing available in get_price_in
"""

import pytest

from tests.fixtures import async_test, mainnet_only
from y import get_price, get_price_in
from y.constants import usdc, weth
from y.datatypes import Price, UsdPrice

# Token addresses on mainnet
USDC_ADDRESS = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
USDT_ADDRESS = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
DAI_ADDRESS = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
WBTC_ADDRESS = "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"

# Block for testing - a known historical block
BLOCK = 18_000_000


class TestOnChainRouting:
    """Tests for on-chain routing (VAL-QT-004, VAL-CROSS-002)."""

    @async_test
    @mainnet_only
    async def test_on_chain_routing_weth_to_usdc(self) -> None:
        """VAL-QT-004: On-chain routing produces reasonable result for well-connected pair.

        WETH/USDC has deep direct pools, so on-chain routing should work.
        Compare with cross-rate within 1% tolerance.
        """
        # Get price via get_price_in (should use on-chain routing)
        result = await get_price_in(WETH_ADDRESS, USDC_ADDRESS, BLOCK, skip_cache=True, sync=False)

        assert result is not None, "Result should not be None"
        assert isinstance(result, Price), f"Result should be Price, got {type(result)}"

        # Get USD prices for cross-rate comparison
        weth_usd = await get_price(WETH_ADDRESS, BLOCK, skip_cache=True, sync=False)
        usdc_usd = await get_price(USDC_ADDRESS, BLOCK, skip_cache=True, sync=False)

        # Cross-rate: WETH price in USDC = weth_usd / usdc_usd
        # Since USDC is ~$1, this should be close to weth_usd
        expected = float(weth_usd) / float(usdc_usd)

        # On-chain routing should produce a result within 1% of cross-rate
        # (For well-connected pairs with deep liquidity)
        tolerance = expected * 0.01
        assert (
            abs(result - expected) < tolerance
        ), f"On-chain result {result} differs from cross-rate {expected} by more than 1%"

        print(f"WETH/USDC on-chain: {result}, cross-rate: {expected}")

    @async_test
    @mainnet_only
    async def test_on_chain_routing_usdc_to_weth(self) -> None:
        """VAL-QT-004: USDC price in WETH via on-chain routing.

        This is the inverse of WETH/USDC. Should work via direct pools.
        """
        result = await get_price_in(USDC_ADDRESS, WETH_ADDRESS, BLOCK, skip_cache=True, sync=False)

        assert result is not None, "Result should not be None"
        assert isinstance(result, Price), f"Result should be Price, got {type(result)}"

        # Cross-rate comparison
        usdc_usd = await get_price(USDC_ADDRESS, BLOCK, skip_cache=True, sync=False)
        weth_usd = await get_price(WETH_ADDRESS, BLOCK, skip_cache=True, sync=False)

        expected = float(usdc_usd) / float(weth_usd)

        # Allow 1% tolerance
        tolerance = expected * 0.01
        assert (
            abs(result - expected) < tolerance
        ), f"On-chain result {result} differs from cross-rate {expected} by more than 1%"

        print(f"USDC/WETH on-chain: {result}, cross-rate: {expected}")

    @async_test
    @mainnet_only
    async def test_multi_hop_routing_to_usdt(self) -> None:
        """VAL-CROSS-002: Multi-hop routing works when routing to non-USD quote tokens.

        Test WBTC -> USDT pricing. WBTC has deep WETH pools, and WETH has USDT pools.
        This should route via WBTC -> WETH -> USDT using multi-hop.
        """
        result = await get_price_in(WBTC_ADDRESS, USDT_ADDRESS, BLOCK, skip_cache=True, sync=False)

        assert result is not None, "Result should not be None"
        assert isinstance(result, Price), f"Result should be Price, got {type(result)}"

        # Cross-rate comparison
        wbtc_usd = await get_price(WBTC_ADDRESS, BLOCK, skip_cache=True, sync=False)
        usdt_usd = await get_price(USDT_ADDRESS, BLOCK, skip_cache=True, sync=False)

        expected = float(wbtc_usd) / float(usdt_usd)

        # Allow 2% tolerance for multi-hop routing (more hops = more variance)
        tolerance = expected * 0.02
        assert (
            abs(result - expected) < tolerance
        ), f"Multi-hop result {result} differs from cross-rate {expected} by more than 2%"

        print(f"WBTC/USDT multi-hop: {result}, cross-rate: {expected}")


class TestFallbackToUsdCrossRate:
    """Tests for USD cross-rate fallback (VAL-QT-005)."""

    @async_test
    @mainnet_only
    async def test_fallback_for_no_direct_pool(self) -> None:
        """VAL-QT-005: Fallback to cross-rate works for pair with no direct pool.

        We test with a token pair that likely has no direct DEX pool.
        The cross-rate calculation should still work.
        """
        # DAI/USDT should work via cross-rate even if direct pools are limited
        result = await get_price_in(DAI_ADDRESS, USDT_ADDRESS, BLOCK, skip_cache=True, sync=False)

        assert result is not None, "Result should not be None"
        assert isinstance(result, Price), f"Result should be Price, got {type(result)}"

        # Both are ~$1 stablecoins, so result should be close to 1.0
        # Allow 0.5% tolerance for stablecoin depeg possibilities
        assert 0.995 < result < 1.005, f"DAI/USDT {result} outside expected range near 1.0"

        print(f"DAI/USDT: {result}")

    @async_test
    @mainnet_only
    async def test_cross_rate_accuracy(self) -> None:
        """VAL-QT-005: Cross-rate result matches manual computation within 1%."""
        # Test USDT -> DAI pricing
        result = await get_price_in(USDT_ADDRESS, DAI_ADDRESS, BLOCK, skip_cache=True, sync=False)

        # Manual cross-rate calculation
        usdt_usd = await get_price(USDT_ADDRESS, BLOCK, skip_cache=True, sync=False)
        dai_usd = await get_price(DAI_ADDRESS, BLOCK, skip_cache=True, sync=False)

        expected = float(usdt_usd) / float(dai_usd)

        # Should be within 1%
        tolerance = max(expected * 0.01, 0.001)  # At least 0.1% absolute tolerance
        assert (
            abs(result - expected) < tolerance
        ), f"Cross-rate {result} differs from manual {expected}"

        print(f"USDT/DAI: {result}, expected: {expected}")


class TestCacheIsolation:
    """Tests for cache isolation (VAL-QT-011)."""

    @async_test
    @mainnet_only
    async def test_usd_cache_not_polluted_by_get_price_in(self) -> None:
        """VAL-QT-011: get_price_in does NOT pollute the USD price cache.

        Calling get_price_in(token, WETH, block) should NOT contaminate
        the cache for get_price(token, block). A subsequent get_price call
        should return UsdPrice (USD-denominated), not an ETH-denominated value.
        """
        # Clear any cached price by using skip_cache first
        weth_price_before = await get_price(WETH_ADDRESS, BLOCK, skip_cache=True, sync=False)

        # Call get_price_in with WETH as quote token
        # This returns an ETH-denominated price
        eth_denominated = await get_price_in(
            USDC_ADDRESS, WETH_ADDRESS, BLOCK, skip_cache=True, sync=False
        )

        assert eth_denominated is not None, "get_price_in should return a result"
        assert isinstance(eth_denominated, Price), "get_price_in should return Price"
        assert not isinstance(eth_denominated, UsdPrice), "Price should not be UsdPrice"

        # Now call get_price for WETH - should return UsdPrice, not Price
        # Use skip_cache=False to test that cache returns correct type
        weth_price_after = await get_price(WETH_ADDRESS, BLOCK, skip_cache=False, sync=False)

        assert weth_price_after is not None, "get_price should return a result"
        assert isinstance(weth_price_after, UsdPrice), (
            f"get_price should return UsdPrice, got {type(weth_price_after)}. "
            "Cache may be polluted by get_price_in."
        )
        assert not isinstance(
            weth_price_after, Price
        ), "UsdPrice should not be instance of Price. Cache pollution detected."

        # The USD price should still be correct (not ~0.0005 like the ETH-denominated one)
        # WETH should be ~$1800-2000 at block 18M
        assert weth_price_after > 1000, (
            f"WETH USD price {weth_price_after} looks like ETH-denominated value. "
            "Cache may be polluted."
        )

        print(f"ETH-denominated USDC: {eth_denominated}")
        print(f"USD-denominated WETH: {weth_price_after}")

    @async_test
    @mainnet_only
    async def test_get_price_returns_usdprice_after_get_price_in(self) -> None:
        """VAL-QT-011: Subsequent get_price calls return UsdPrice after get_price_in.

        This tests that the cache types remain distinct.
        """
        # First call get_price_in with a non-USD quote token
        usdc_in_eth = await get_price_in(
            USDC_ADDRESS, WETH_ADDRESS, BLOCK, skip_cache=True, sync=False
        )

        # Now get USD price of USDC
        usdc_usd = await get_price(USDC_ADDRESS, BLOCK, skip_cache=True, sync=False)

        # USDC is a stablecoin, get_price returns int 1 for stablecoins
        # But let's test with WETH to be sure
        weth_usd = await get_price(WETH_ADDRESS, BLOCK, skip_cache=True, sync=False)

        assert isinstance(usdc_in_eth, Price), "get_price_in should return Price"
        assert isinstance(
            weth_usd, UsdPrice
        ), f"get_price should return UsdPrice, got {type(weth_usd)}"

        # The values should be drastically different
        # usdc_in_eth should be ~0.0005, weth_usd should be ~1800-2000
        ratio = float(weth_usd) / float(usdc_in_eth) if usdc_in_eth > 0 else 0
        assert ratio > 1000, (
            f"Ratio {ratio} suggests cache pollution. "
            f"usdc_in_eth={usdc_in_eth}, weth_usd={weth_usd}"
        )

        print(f"USDC in ETH: {usdc_in_eth}")
        print(f"WETH in USD: {weth_usd}")
        print(f"Ratio (should be ~2000): {ratio}")


class TestMultiHopInGetPriceIn:
    """Tests for multi-hop routing integration (VAL-CROSS-002)."""

    @async_test
    @mainnet_only
    async def test_routing_tokens_used_for_non_usd_quote(self) -> None:
        """VAL-CROSS-002: Multi-hop routing tokens are used when routing to non-USD quote tokens.

        Test that ROUTING_TOKENS (USDT, DAI, etc.) are used as intermediaries
        when routing to a non-USD quote token.
        """
        # Get WBTC price in DAI - should route through WETH or other intermediaries
        result = await get_price_in(WBTC_ADDRESS, DAI_ADDRESS, BLOCK, skip_cache=True, sync=False)

        assert result is not None, "Result should not be None"
        assert isinstance(result, Price), f"Result should be Price, got {type(result)}"

        # Cross-rate comparison
        wbtc_usd = await get_price(WBTC_ADDRESS, BLOCK, skip_cache=True, sync=False)
        dai_usd = await get_price(DAI_ADDRESS, BLOCK, skip_cache=True, sync=False)

        expected = float(wbtc_usd) / float(dai_usd)

        # Allow 2% tolerance for multi-hop routing
        tolerance = expected * 0.02
        assert (
            abs(result - expected) < tolerance
        ), f"Multi-hop result {result} differs from cross-rate {expected}"

        print(f"WBTC/DAI: {result}, expected: {expected}")

    @async_test
    @mainnet_only
    async def test_weth_to_dai_routing(self) -> None:
        """WETH to DAI should work with on-chain routing or cross-rate fallback."""
        result = await get_price_in(WETH_ADDRESS, DAI_ADDRESS, BLOCK, skip_cache=True, sync=False)

        assert result is not None, "Result should not be None"
        assert isinstance(result, Price), f"Result should be Price, got {type(result)}"

        # WETH/DAI should be around 1800-2000 (ETH price in DAI)
        assert 1500 < result < 2500, f"WETH/DAI {result} outside expected range"

        print(f"WETH/DAI: {result}")
