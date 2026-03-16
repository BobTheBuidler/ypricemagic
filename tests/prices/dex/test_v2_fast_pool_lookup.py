"""Tests for V2 pool lookup.

Previously these tested get_pools_via_factory_getpair(), which has been removed
in favour of the inverted pool index (_pool_index). The remaining test verifies
that get_pools_for() still finds MIC/USDT quickly via the index.

Key test: MIC at block 12500000 should find its USDT pool quickly via the index.
"""

import pytest

from tests.fixtures import async_test, mainnet_only
from y.prices.dex.uniswap.v2 import UniswapRouterV2

# Well-known mainnet addresses
USDT = "0xdAC17F958D2ee523a2206206994597C13D831ec7"

# MIC (Mithril Cash) - only has a USDT pool at early blocks
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
async def test_get_pools_for_uses_index_on_mainnet(uniswap_v2_router: UniswapRouterV2) -> None:
    """Verify that get_pools_for() uses the inverted index on mainnet.

    On mainnet, _supports_factory_helper is False so get_pools_for() falls
    through to the index-based all_pools_for(). The inverted index knows about
    every pool including MIC/USDT, so the result should be non-empty and fast.
    """
    # Verify that mainnet has _supports_factory_helper = False (as expected)
    assert uniswap_v2_router._supports_factory_helper is False, (
        "On mainnet, _supports_factory_helper should be False "
        "(mainnet bypasses the factory helper due to too many pools)"
    )

    # get_pools_for() should return results via the inverted index
    pools = await uniswap_v2_router.get_pools_for(MIC_ADDRESS, block=MIC_TEST_BLOCK, sync=False)

    assert (
        pools
    ), f"get_pools_for should find MIC pools at block {MIC_TEST_BLOCK} via the inverted index. "

    paired_tokens_lower = {str(addr).lower() for addr in pools.values()}
    assert USDT.lower() in paired_tokens_lower, (
        f"Expected MIC/USDT pool from get_pools_for(). "
        f"Found paired tokens: {paired_tokens_lower}"
    )
