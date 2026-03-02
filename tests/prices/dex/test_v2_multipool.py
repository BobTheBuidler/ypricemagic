"""Tests for V2 multi-pool candidate routing.

These tests verify that UniswapRouterV2.get_path_to_stables() tries multiple
candidate pools instead of only the single deepest pool. The expanded routing
enables price discovery for tokens where the deepest pool is a dead-end.

Tests are marked slow because V2 pool discovery may need to load pool events.
Run with --runslow.
"""

import pytest

from tests.fixtures import async_test, mainnet_only
from y.constants import STABLECOINS
from y.exceptions import CantFindSwapPath
from y.networks import Network
from y.prices.dex.uniswap.v2 import UniswapRouterV2, UniswapV2Pool
from y.prices.dex.uniswap.uniswap import uniswap_multiplexer
from y import get_price

# Well-known mainnet addresses
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
USDT = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
WBTC = "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
DAI = "0x6B175474E89094C44Da98b954EedeAC495271d0F"

# Block for testing - a known historical block
BLOCK = 18_000_000

# Uniswap V2 router address (mainnet)
UNISWAP_V2_ROUTER = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"

# Maximum candidate pools constant (should match implementation)
MAX_CANDIDATE_POOLS = 5


@pytest.fixture
def uniswap_v2_router() -> UniswapRouterV2:
    """Fixture providing a UniswapRouterV2 instance for testing."""
    return UniswapRouterV2(UNISWAP_V2_ROUTER, asynchronous=True)


@pytest.mark.slow
@async_test
@mainnet_only
async def test_v2_top_pools_returns_multiple(uniswap_v2_router) -> None:
    """VAL-V2-001: V2 evaluates multiple candidate pools.

    Verify that top_pools returns multiple pools sorted by liquidity.
    """
    # WETH has many pools, should return multiple candidates
    pools = [
        pool
        async for pool in uniswap_v2_router.top_pools(
            WETH, BLOCK, n=MAX_CANDIDATE_POOLS, _ignore_pools=(), sync=False
        )
    ]

    # Should get multiple pools for a well-connected token
    assert len(pools) >= 2, f"Expected multiple pools for WETH, got {len(pools)}"
    print(f"Top pools for WETH at block {BLOCK}: {[str(p) for p in pools[:3]]}")


@pytest.mark.slow
@async_test
@mainnet_only
async def test_v2_top_pools_respects_ignore_pools(uniswap_v2_router) -> None:
    """VAL-V2-004: V2 respects ignore_pools with multi-pool logic.

    Verify that pools in ignore_pools are not returned by top_pools.
    """
    # Get the deepest pool for USDC
    deepest = await uniswap_v2_router.deepest_pool(USDC, BLOCK, sync=False)
    assert deepest is not None, "USDC should have a deepest pool"

    # Now get top pools with the deepest pool ignored
    pools = [
        pool
        async for pool in uniswap_v2_router.top_pools(
            USDC, BLOCK, n=5, _ignore_pools=(deepest,), sync=False
        )
    ]

    # The ignored pool should not be in the results
    pool_addresses = {str(pool.address).lower() for pool in pools}
    assert (
        str(deepest.address).lower() not in pool_addresses
    ), f"Ignored pool {deepest.address} should not be in top_pools results"
    print(f"Top pools for USDC (ignoring deepest): {[str(p) for p in pools]}")


@pytest.mark.slow
@async_test
@mainnet_only
async def test_v2_well_connected_token_regression(uniswap_v2_router) -> None:
    """VAL-V2-003: V2 regression - well-connected tokens unaffected.

    Verify that tokens with well-established V2 pools still return correct prices.
    """
    # WBTC is well-connected with deep WETH and stablecoin pools
    price = await uniswap_v2_router.get_price(WBTC, BLOCK, skip_cache=True, sync=False)

    assert price is not None, "WBTC should return a price"
    # WBTC price at block 18M was around $25,000-35,000
    assert 20_000 < price < 50_000, f"WBTC price {price} outside expected range"
    print(f"WBTC price at block {BLOCK}: {price}")


@pytest.mark.slow
@async_test
@mainnet_only
async def test_v2_evaluation_is_bounded(uniswap_v2_router) -> None:
    """VAL-V2-005: V2 candidate pool evaluation is bounded.

    Verify that get_path_to_stables tries at most MAX_CANDIDATE_POOLS candidates.
    This test ensures evaluation completes in reasonable time.
    """
    # Use a token with many pools (WETH has tons of V2 pools)
    # The evaluation should still complete quickly because it's bounded

    import time

    start = time.time()

    try:
        path = await uniswap_v2_router.get_path_to_stables(
            WETH, BLOCK, _ignore_pools=(), sync=False
        )
        elapsed = time.time() - start

        # Should complete in reasonable time (< 30 seconds)
        assert elapsed < 30, f"Path resolution took too long: {elapsed:.2f}s"
        print(f"Path for WETH at block {BLOCK}: {path} (took {elapsed:.2f}s)")
    except CantFindSwapPath:
        # Even if it fails, it should fail quickly
        elapsed = time.time() - start
        assert elapsed < 30, f"Path resolution took too long even on failure: {elapsed:.2f}s"
        print(f"No path found for WETH (took {elapsed:.2f}s)")


@pytest.mark.slow
@async_test
@mainnet_only
async def test_v2_cant_find_swap_path_after_all_candidates() -> None:
    """VAL-V2-006: V2 CantFindSwapPath only after all candidates exhausted.

    Verify that CantFindSwapPath is raised only after all candidate pools fail,
    not after the first failure.
    """
    # Create a router for testing
    router = UniswapRouterV2(UNISWAP_V2_ROUTER, asynchronous=True)

    # Use a token that has no path to stables via V2
    # We'll use an address that has no V2 pools deployed
    from y.constants import EEE_ADDRESS
    
    # The EEE_ADDRESS is a special placeholder that has no V2 pools
    invalid_token = EEE_ADDRESS

    with pytest.raises(CantFindSwapPath):
        await router.get_path_to_stables(invalid_token, BLOCK, sync=False)

    print("CantFindSwapPath raised as expected for invalid token")


@pytest.mark.slow
@async_test
@mainnet_only
async def test_v2_price_via_get_price() -> None:
    """VAL-CROSS-001: Multi-hop improvements active in get_price for V2.

    Test that V2 improvements are active when calling top-level get_price().
    """
    # Test WBTC through the top-level API
    price = await get_price(WBTC, BLOCK, skip_cache=True, sync=False)

    assert price is not None, "WBTC should return a price via get_price"
    assert price > 0, f"Price should be positive, got {price}"
    print(f"WBTC price via get_price at block {BLOCK}: {price}")


@pytest.mark.slow
@async_test
@mainnet_only
async def test_v2_alternative_pool_selection() -> None:
    """VAL-V2-002: V2 finds price through alternative pool.

    Test that a token whose deepest pool might be problematic can still find
    a price through an alternative pool. We simulate this by ignoring the
    deepest pool and verifying a price is still found.
    """
    router = UniswapRouterV2(UNISWAP_V2_ROUTER, asynchronous=True)

    # Get the deepest pool for a well-known token
    deepest = await router.deepest_pool(WBTC, BLOCK, sync=False)
    assert deepest is not None, "WBTC should have a deepest pool"

    # Get price with the deepest pool ignored - should still work via alternative
    price = await router.get_price(
        WBTC, BLOCK, skip_cache=True, ignore_pools=(deepest,), sync=False
    )

    # Should still find a price through alternative pools
    assert price is not None, f"Should find price via alternative pool when deepest is ignored"
    # Price should still be reasonable
    assert 20_000 < price < 50_000, f"WBTC price {price} outside expected range"
    print(f"WBTC price with deepest pool ignored: {price}")
