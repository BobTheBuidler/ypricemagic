"""Tests for amount-aware V3 liquidity threshold.

SPELL (0x090185f2135308BaD17527004364eBcC2D37e5F6) at block 18,000,000 has a V3
WETH pool (fee=3000) with ~7.75 ETH of WETH — below the 10 ETH (10**19 wei)
threshold in UniswapV3.check_liquidity — but ~169M SPELL tokens on the token side.

Without an amount, the threshold rejects the pool.  With an amount that fits
the token-side liquidity, the pool should be accepted.

These tests are marked slow because V3 pool discovery scans PoolCreated events
which is inherently slow against a remote archive node.  Run with --runslow.
"""

import pytest

from tests.fixtures import async_test, mainnet_only
from y.prices.dex.uniswap.uniswap import uniswap_multiplexer
from y.prices.dex.uniswap.v3 import UniswapV3

SPELL = "0x090185f2135308BaD17527004364eBcC2D37e5F6"
BLOCK = 18_000_000
AMOUNT = 1000  # 1000 SPELL tokens — well within the ~169M available


@pytest.mark.slow
@async_test
@mainnet_only
async def test_v3_check_liquidity_rejects_without_amount() -> None:
    """VAL-LIQ-002: threshold still rejects small WETH pools for unit queries."""
    v3 = uniswap_multiplexer.v3
    assert v3 is not None
    liquidity = await v3.check_liquidity(SPELL, BLOCK, sync=False)
    assert liquidity == 0, f"Expected 0 (threshold rejection), got {liquidity}"


@pytest.mark.slow
@async_test
@mainnet_only
async def test_v3_check_liquidity_accepts_with_amount() -> None:
    """VAL-LIQ-001: threshold accepts pools when amount fits token-side liquidity."""
    v3 = uniswap_multiplexer.v3
    assert v3 is not None
    liquidity = await v3.check_liquidity(SPELL, BLOCK, amount=AMOUNT, sync=False)
    assert liquidity > 0, f"Expected >0 (amount should bypass threshold), got {liquidity}"


@pytest.mark.slow
@async_test
@mainnet_only
async def test_routers_by_depth_includes_v3_with_amount() -> None:
    """VAL-LIQ-003: amount flows through multiplexer to V3 pool selection."""
    routers_without = await uniswap_multiplexer.routers_by_depth(SPELL, block=BLOCK, sync=False)
    routers_with = await uniswap_multiplexer.routers_by_depth(
        SPELL, block=BLOCK, amount=AMOUNT, sync=False
    )
    has_v3_without = any(isinstance(r, UniswapV3) for r in routers_without)
    has_v3_with = any(isinstance(r, UniswapV3) for r in routers_with)
    assert not has_v3_without, "V3 should be filtered out without amount"
    assert has_v3_with, "V3 should be included when amount fits"
