"""CI tests: V2 price correctness and timing after the inverted-index migration.

These tests verify:
- get_price() returns correct prices for major tokens (WETH, WBTC, UNI, LINK)
  at block 19000000.
- get_price() resolves MIC via the multi-hop USDT→USDC path at block 12500000.
- Index-backed all_pools_for() is O(1) — each lookup completes in <10 ms after
  the index is built (measured against the per-lookup wall-clock, not total
  startup time).

Tests are marked slow and mainnet-only.  They will not run locally on macOS;
they are intended for the Linux/Docker CI environment.

References:
    VAL-V2IDX-003: get_price() correct for major tokens (WETH, WBTC, UNI, LINK)
    VAL-V2IDX-004: get_price() correct for MIC via multi-hop path
    VAL-V2IDX-005: Index lookup is O(1), <10 ms
"""

import time

import pytest

from tests.fixtures import async_test, mainnet_only
from y import get_price
from y.prices.dex.uniswap.v2 import UniswapRouterV2

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Well-known mainnet token addresses
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
WBTC = "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
UNI = "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"
LINK = "0x514910771AF9Ca656af840dff83E8264EcF986CA"

# MIC (Mithril Cash) — resolves via V2 multi-hop: MIC→USDT→USDC
MIC = "0x368B3a58B5f49392e5C9E4C998cb0bB966752E51"

# Block numbers
MAJOR_TOKEN_BLOCK = 19_000_000
MIC_BLOCK = 12_500_000

# Uniswap V2 mainnet router
UNISWAP_V2_ROUTER = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"

# Expected price ranges at MAJOR_TOKEN_BLOCK (generous bounds to account for
# minor price differences across routing paths)
WETH_RANGE = (2_000, 3_500)
WBTC_RANGE = (40_000, 70_000)
UNI_RANGE = (5, 15)
LINK_RANGE = (10, 25)

# Maximum acceptable per-lookup time (ms) for index-backed lookups.
# The old O(N) scan over 330k+ pools took hundreds of ms to seconds; the
# O(1) dict lookup must be well under this threshold.
MAX_LOOKUP_MS = 10.0


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def v2_router() -> UniswapRouterV2:
    """Async UniswapRouterV2 instance for the mainnet Uniswap V2 deployment."""
    return UniswapRouterV2(UNISWAP_V2_ROUTER, asynchronous=True)


# ---------------------------------------------------------------------------
# VAL-V2IDX-003: Price correctness — WETH
# ---------------------------------------------------------------------------


@pytest.mark.slow
@async_test
@mainnet_only
async def test_weth_price_correct_at_block_19m() -> None:
    """VAL-V2IDX-003: WETH price is in the expected range at block 19000000.

    After the inverted-index migration, get_price() must still return a
    sensible WETH price.  At block 19000000 WETH traded around $2200–$2800.
    """
    price = await get_price(WETH, MAJOR_TOKEN_BLOCK, skip_cache=True, sync=False)
    lo, hi = WETH_RANGE
    assert price is not None, "WETH price must not be None"
    assert lo < price < hi, (
        f"WETH price {price:.2f} outside expected range [{lo}, {hi}] "
        f"at block {MAJOR_TOKEN_BLOCK}"
    )
    print(f"WETH at block {MAJOR_TOKEN_BLOCK}: ${price:.2f}")


# ---------------------------------------------------------------------------
# VAL-V2IDX-003: Price correctness — WBTC
# ---------------------------------------------------------------------------


@pytest.mark.slow
@async_test
@mainnet_only
async def test_wbtc_price_correct_at_block_19m() -> None:
    """VAL-V2IDX-003: WBTC price is in the expected range at block 19000000.

    At block 19000000 WBTC traded around $42,000–$52,000.
    """
    price = await get_price(WBTC, MAJOR_TOKEN_BLOCK, skip_cache=True, sync=False)
    lo, hi = WBTC_RANGE
    assert price is not None, "WBTC price must not be None"
    assert lo < price < hi, (
        f"WBTC price {price:.2f} outside expected range [{lo}, {hi}] "
        f"at block {MAJOR_TOKEN_BLOCK}"
    )
    print(f"WBTC at block {MAJOR_TOKEN_BLOCK}: ${price:.2f}")


# ---------------------------------------------------------------------------
# VAL-V2IDX-003: Price correctness — UNI
# ---------------------------------------------------------------------------


@pytest.mark.slow
@async_test
@mainnet_only
async def test_uni_price_correct_at_block_19m() -> None:
    """VAL-V2IDX-003: UNI price is in the expected range at block 19000000.

    At block 19000000 UNI traded around $6–$10.
    """
    price = await get_price(UNI, MAJOR_TOKEN_BLOCK, skip_cache=True, sync=False)
    lo, hi = UNI_RANGE
    assert price is not None, "UNI price must not be None"
    assert lo < price < hi, (
        f"UNI price {price:.2f} outside expected range [{lo}, {hi}] "
        f"at block {MAJOR_TOKEN_BLOCK}"
    )
    print(f"UNI at block {MAJOR_TOKEN_BLOCK}: ${price:.2f}")


# ---------------------------------------------------------------------------
# VAL-V2IDX-003: Price correctness — LINK
# ---------------------------------------------------------------------------


@pytest.mark.slow
@async_test
@mainnet_only
async def test_link_price_correct_at_block_19m() -> None:
    """VAL-V2IDX-003: LINK price is in the expected range at block 19000000.

    At block 19000000 LINK traded around $14–$20.
    """
    price = await get_price(LINK, MAJOR_TOKEN_BLOCK, skip_cache=True, sync=False)
    lo, hi = LINK_RANGE
    assert price is not None, "LINK price must not be None"
    assert lo < price < hi, (
        f"LINK price {price:.2f} outside expected range [{lo}, {hi}] "
        f"at block {MAJOR_TOKEN_BLOCK}"
    )
    print(f"LINK at block {MAJOR_TOKEN_BLOCK}: ${price:.2f}")


# ---------------------------------------------------------------------------
# VAL-V2IDX-004: MIC multi-hop via USDT
# ---------------------------------------------------------------------------


@pytest.mark.slow
@async_test
@mainnet_only
async def test_mic_price_via_multihop_at_block_12_5m() -> None:
    """VAL-V2IDX-004: MIC resolves via multi-hop USDT path at block 12500000.

    MIC (Mithril Cash) only has a direct V2 pool with USDT (not with USDC or
    WETH directly at this block).  After the inverted-index migration the pool
    lookup finds MIC/USDT, then continues via USDT→USDC, giving a non-zero
    price.  The old get_pools_via_factory_getpair() fast path would have missed
    this pool.
    """
    price = await get_price(MIC, MIC_BLOCK, skip_cache=True, sync=False)
    assert price is not None, "MIC price must not be None at block 12500000"
    assert price > 0, f"MIC price must be positive, got {price}"
    print(f"MIC at block {MIC_BLOCK}: ${price:.6f}")


# ---------------------------------------------------------------------------
# VAL-V2IDX-005: O(1) timing assertion
# ---------------------------------------------------------------------------


@pytest.mark.slow
@async_test
@mainnet_only
async def test_index_lookup_is_fast_after_warmup(v2_router: UniswapRouterV2) -> None:
    """VAL-V2IDX-005: Index-backed all_pools_for() is O(1), <10 ms per lookup.

    The old O(N) linear scan over 330k+ pools took hundreds of milliseconds to
    seconds.  After the inverted-index migration each lookup is a dict access
    and must complete in under 10 ms (once the index is built).

    This test:
      1. Warms up the index by awaiting __pool_index__.
      2. Times individual all_pools_for() calls for several tokens.
      3. Asserts each lookup completes in < 10 ms.
    """
    # Step 1: Build (or fetch) the index.  This may take seconds on first run.
    _index = await v2_router.__pool_index__
    assert _index, "Index must be non-empty after warm-up"

    # Step 2: Time individual lookups.
    sample_tokens = [WETH, WBTC, UNI, LINK]
    for token in sample_tokens:
        t_start = time.perf_counter()
        pools = await v2_router.all_pools_for(token, sync=False)
        elapsed_ms = (time.perf_counter() - t_start) * 1000
        print(
            f"  all_pools_for({token[:8]}…): {len(pools)} pools in {elapsed_ms:.2f} ms"
        )
        assert elapsed_ms < MAX_LOOKUP_MS, (
            f"Index lookup for {token} took {elapsed_ms:.2f} ms "
            f"(threshold {MAX_LOOKUP_MS} ms). "
            "The inverted index O(1) lookup should be sub-millisecond after build."
        )
