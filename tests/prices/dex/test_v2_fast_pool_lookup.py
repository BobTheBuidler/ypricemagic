"""Tests for V2 fast pool lookup via factory.getPair().

These tests verify that UniswapRouterV2.get_pools_via_factory_getpair() correctly
finds pools using the O(1) factory.getPair() view function instead of scanning
all 330k+ pairs.

Key test: MIC at block 12500000 should find its USDT pool quickly via getPair.
"""

import pytest

from tests.fixtures import async_test, mainnet_only
from y.prices.dex.uniswap.v2 import UniswapRouterV2

# Well-known mainnet addresses
USDT = "0xdAC17F958D2ee523a2206206994597C13D831ec7"

# MIC (Mithril Cash) - only has a USDT pool at early blocks
# factory.getPair(MIC, USDT) returns a non-zero address at block 12500000
MIC_ADDRESS = "0x368B3a58B5f49392e5C9E4C998cb0bB966752E51"
MIC_TEST_BLOCK = 12_500_000

# Uniswap V2 router address (mainnet)
UNISWAP_V2_ROUTER = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"


@pytest.fixture
def uniswap_v2_router() -> UniswapRouterV2:
    """Fixture providing a UniswapRouterV2 instance for testing."""
    return UniswapRouterV2(UNISWAP_V2_ROUTER, asynchronous=True)


@async_test
@mainnet_only
async def test_fast_pool_lookup(uniswap_v2_router: UniswapRouterV2) -> None:
    """Verify fast pool lookup finds MIC/USDT pool via getPair() at block 12500000.

    At block 12500000, MIC (Mithril Cash) only has a USDT pool on Uniswap V2.
    The factory.getPair(MIC, USDT) returns a non-zero address. This test verifies
    that get_pools_via_factory_getpair() finds this pool without scanning all pairs.
    """
    pools = await uniswap_v2_router.get_pools_via_factory_getpair(
        MIC_ADDRESS, block=MIC_TEST_BLOCK, sync=False
    )

    assert pools, (
        f"get_pools_via_factory_getpair should find MIC pools at block {MIC_TEST_BLOCK}, "
        f"but returned empty dict. Expected to find MIC/USDT pool."
    )

    # There should be at least one pool
    assert len(pools) >= 1, f"Expected at least 1 pool for MIC, got {len(pools)}"

    # The paired tokens should include USDT (case-insensitive check)
    paired_tokens_lower = {str(addr).lower() for addr in pools.values()}
    assert USDT.lower() in paired_tokens_lower, (
        f"Expected MIC/USDT pool to be found via getPair(). "
        f"Found pools with paired tokens: {paired_tokens_lower}"
    )

    print(f"Found {len(pools)} pool(s) for MIC at block {MIC_TEST_BLOCK} via getPair:")
    for pool, token_out in pools.items():
        print(f"  Pool: {pool.address}, Token out: {token_out}")


@async_test
@mainnet_only
async def test_get_pools_for_uses_fast_path_on_mainnet(uniswap_v2_router: UniswapRouterV2) -> None:
    """Verify that get_pools_for() uses the fast getPair path on mainnet.

    On mainnet, _supports_factory_helper is False, so get_pools_for() should
    call get_pools_via_factory_getpair() first rather than all_pools_for().
    Since MIC only has a USDT pool, if the fast path works, we'll find it;
    if it falls back to all_pools_for() it will take 10+ minutes.
    """
    # Verify that mainnet has _supports_factory_helper = False (as expected)
    assert uniswap_v2_router._supports_factory_helper is False, (
        "On mainnet, _supports_factory_helper should be False "
        "(mainnet bypasses the factory helper due to too many pools)"
    )

    # get_pools_for() should return results quickly via the fast path
    pools = await uniswap_v2_router.get_pools_for(MIC_ADDRESS, block=MIC_TEST_BLOCK, sync=False)

    assert pools, (
        f"get_pools_for should find MIC pools at block {MIC_TEST_BLOCK} via fast getPair path. "
        f"If this hangs, the fallback to all_pools_for() is being incorrectly triggered."
    )

    paired_tokens_lower = {str(addr).lower() for addr in pools.values()}
    assert USDT.lower() in paired_tokens_lower, (
        f"Expected MIC/USDT pool from get_pools_for(). "
        f"Found paired tokens: {paired_tokens_lower}"
    )
