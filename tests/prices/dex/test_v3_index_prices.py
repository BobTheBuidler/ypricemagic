"""CI tests: V3 price correctness and index behavior after the inverted-index migration.

These tests verify:
- uniswap_v3.get_price() returns correct prices for major V3-traded tokens
  (WETH, UNI, AAVE, MATIC) at block 18_000_000.
- get_price() returns the same correct prices through the top-level magic API.
- _BoundedPoolsByTokenCache is removed; _pool_index is present on UniV3Pools.
- pools_for_token() yields correct UniswapV3Pool objects for WETH at the test block.
- Index-backed pools_for_token() lookup is O(1) — each call completes in <10 ms
  after the index is built (measured against per-lookup wall-clock, not total
  startup time).

Tests are marked slow and mainnet-only.  They will not run locally on macOS;
they are intended for the Linux/Docker CI environment.

References:
    VAL-V3IDX-010: get_price() correct for major V3 tokens (WETH, UNI, AAVE, MATIC)
    VAL-V3IDX-011: _BoundedPoolsByTokenCache absent; _pool_index present on UniV3Pools
    VAL-V3IDX-012: pools_for_token() returns pools correctly via O(1) index
"""

import time

import pytest

from tests.fixtures import async_test, mainnet_only
from y import get_price
from y.prices.dex.uniswap.v3 import UniV3Pools, UniswapV3Pool, uniswap_v3

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Well-known mainnet token addresses
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
UNI = "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"
AAVE = "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9"

# MATIC (ERC-20 on Ethereum mainnet, bridged MATIC)
# Has V3 liquidity (MATIC/WETH, MATIC/USDC pools) from mid-2021 onward
MATIC = "0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0"

# Test block — all tokens above have V3 liquidity here
V3_BLOCK = 18_000_000

# Expected price ranges at V3_BLOCK (generous to avoid flakiness)
WETH_RANGE = (1_500, 3_000)
UNI_RANGE = (3, 15)
AAVE_RANGE = (50, 150)
MATIC_RANGE = (0.4, 1.5)

# Maximum acceptable per-lookup time (ms) for index-backed lookups.
# The old O(N) scan over ~170k+ V3 pools took hundreds of ms to seconds;
# the O(1) dict lookup must be well under this threshold.
MAX_LOOKUP_MS = 10.0


# ---------------------------------------------------------------------------
# VAL-V3IDX-010: Price correctness — WETH via V3
# ---------------------------------------------------------------------------


@pytest.mark.slow
@async_test
@mainnet_only
async def test_weth_price_via_v3_at_block_18m() -> None:
    """VAL-V3IDX-010: WETH price is in the expected range at block 18_000_000 via V3.

    After the inverted-index migration, uniswap_v3.get_price() must still return
    a sensible WETH price.  At block 18_000_000 WETH traded around $1600–$2000.
    """
    assert uniswap_v3 is not None, "uniswap_v3 should exist on mainnet"
    price = await uniswap_v3.get_price(WETH, V3_BLOCK, skip_cache=True, sync=False)
    lo, hi = WETH_RANGE
    assert price is not None, "WETH price must not be None via V3"
    assert lo < price < hi, (
        f"WETH price {price:.2f} outside expected range [{lo}, {hi}] " f"at block {V3_BLOCK}"
    )
    print(f"WETH via V3 at block {V3_BLOCK}: ${price:.2f}")


# ---------------------------------------------------------------------------
# VAL-V3IDX-010: Price correctness — UNI via V3
# ---------------------------------------------------------------------------


@pytest.mark.slow
@async_test
@mainnet_only
async def test_uni_price_via_v3_at_block_18m() -> None:
    """VAL-V3IDX-010: UNI price is in the expected range at block 18_000_000 via V3.

    UNI has a WETH/UNI V3 pool (fee=3000) with strong liquidity.  At block
    18_000_000 UNI traded around $5–$9.
    """
    assert uniswap_v3 is not None, "uniswap_v3 should exist on mainnet"
    price = await uniswap_v3.get_price(UNI, V3_BLOCK, skip_cache=True, sync=False)
    lo, hi = UNI_RANGE
    assert price is not None, "UNI price must not be None via V3"
    assert lo < price < hi, (
        f"UNI price {price:.2f} outside expected range [{lo}, {hi}] " f"at block {V3_BLOCK}"
    )
    print(f"UNI via V3 at block {V3_BLOCK}: ${price:.2f}")


# ---------------------------------------------------------------------------
# VAL-V3IDX-010: Price correctness — AAVE via V3
# ---------------------------------------------------------------------------


@pytest.mark.slow
@async_test
@mainnet_only
async def test_aave_price_via_v3_at_block_18m() -> None:
    """VAL-V3IDX-010: AAVE price is in the expected range at block 18_000_000 via V3.

    AAVE has a WETH/AAVE V3 pool (fee=3000) with reasonable liquidity.  At
    block 18_000_000 AAVE traded around $65–$90.
    """
    assert uniswap_v3 is not None, "uniswap_v3 should exist on mainnet"
    price = await uniswap_v3.get_price(AAVE, V3_BLOCK, skip_cache=True, sync=False)
    lo, hi = AAVE_RANGE
    assert price is not None, "AAVE price must not be None via V3"
    assert lo < price < hi, (
        f"AAVE price {price:.2f} outside expected range [{lo}, {hi}] " f"at block {V3_BLOCK}"
    )
    print(f"AAVE via V3 at block {V3_BLOCK}: ${price:.2f}")


# ---------------------------------------------------------------------------
# VAL-V3IDX-010: Price correctness — MATIC via top-level get_price()
# ---------------------------------------------------------------------------


@pytest.mark.slow
@async_test
@mainnet_only
async def test_matic_price_via_get_price_at_block_18m() -> None:
    """VAL-V3IDX-010: MATIC price correct at block 18_000_000 via top-level get_price().

    MATIC (ERC-20 on Ethereum mainnet) has V3 liquidity (MATIC/WETH, MATIC/USDC).
    At block 18_000_000 MATIC traded around $0.55–$0.80.
    """
    price = await get_price(MATIC, V3_BLOCK, skip_cache=True, sync=False)
    lo, hi = MATIC_RANGE
    assert price is not None, "MATIC price must not be None at block 18_000_000"
    assert lo < price < hi, (
        f"MATIC price {price:.4f} outside expected range [{lo}, {hi}] " f"at block {V3_BLOCK}"
    )
    print(f"MATIC at block {V3_BLOCK}: ${price:.4f}")


# ---------------------------------------------------------------------------
# VAL-V3IDX-011: Structural — _BoundedPoolsByTokenCache removed; _pool_index present
# ---------------------------------------------------------------------------


@pytest.mark.slow
@async_test
@mainnet_only
async def test_bounded_pool_cache_removed_pool_index_present() -> None:
    """VAL-V3IDX-011: _BoundedPoolsByTokenCache is gone; UniV3Pools has _pool_index.

    After the inverted-index migration:
    - The v3 module must NOT export _BoundedPoolsByTokenCache.
    - UniV3Pools instances must have a _pool_index dict attribute.
    """
    import y.prices.dex.uniswap.v3 as v3_module

    assert not hasattr(
        v3_module, "_BoundedPoolsByTokenCache"
    ), "_BoundedPoolsByTokenCache should be removed from v3 module after refactoring"

    assert uniswap_v3 is not None, "uniswap_v3 should exist on mainnet"
    pools_obj = await uniswap_v3.__pools__
    assert isinstance(
        pools_obj, UniV3Pools
    ), f"__pools__ should be a UniV3Pools instance, got {type(pools_obj)}"
    assert hasattr(
        pools_obj, "_pool_index"
    ), "UniV3Pools instance should have _pool_index after refactoring"
    assert isinstance(
        pools_obj._pool_index, dict
    ), f"_pool_index should be a dict, got {type(pools_obj._pool_index)}"
    print(
        f"_BoundedPoolsByTokenCache absent; "
        f"_pool_index present with {len(pools_obj._pool_index)} token entries"
    )


# ---------------------------------------------------------------------------
# VAL-V3IDX-012: pools_for_token() yields correct pools for WETH via index
# ---------------------------------------------------------------------------


@pytest.mark.slow
@async_test
@mainnet_only
async def test_pools_for_token_yields_weth_pools() -> None:
    """VAL-V3IDX-012: pools_for_token() yields UniswapV3Pool objects for WETH.

    After the inverted-index migration, pools_for_token() must:
    1. Return at least one pool for WETH at block V3_BLOCK.
    2. Each yielded object must be a UniswapV3Pool instance.
    3. Each pool must have WETH as one of its tokens.
    """
    assert uniswap_v3 is not None, "uniswap_v3 should exist on mainnet"

    found_pools: list[UniswapV3Pool] = []
    async for pool in uniswap_v3.pools_for_token(WETH, V3_BLOCK):
        assert isinstance(
            pool, UniswapV3Pool
        ), f"pools_for_token should yield UniswapV3Pool, got {type(pool)}"
        # WETH must be one of the pool's tokens
        weth_lower = WETH.lower()
        assert (
            str(pool.token0.address).lower() == weth_lower
            or str(pool.token1.address).lower() == weth_lower
        ), f"Pool {pool.address} should contain WETH but has tokens {pool.token0} / {pool.token1}"
        found_pools.append(pool)

    assert found_pools, f"pools_for_token should return pools for WETH at block {V3_BLOCK}"
    print(f"pools_for_token returned {len(found_pools)} pools for WETH at block {V3_BLOCK}")


# ---------------------------------------------------------------------------
# VAL-V3IDX-012: Index-backed pools_for_token() is O(1) — sub-millisecond after build
# ---------------------------------------------------------------------------


@pytest.mark.slow
@async_test
@mainnet_only
async def test_pools_for_token_is_fast_after_warmup() -> None:
    """VAL-V3IDX-012: pools_for_token() is O(1) fast after the index is built.

    The old O(N) iteration over ~170k+ pools took hundreds of milliseconds.
    After the inverted-index migration, each pools_for_token() call is a dict
    lookup and must complete in under 10 ms once the index is warmed up.

    This test:
    1. Warms the index by awaiting __pools__ (which builds _pool_index).
    2. Times individual pools_for_token() calls for WETH and UNI.
    3. Asserts each call completes in < MAX_LOOKUP_MS.
    """
    assert uniswap_v3 is not None, "uniswap_v3 should exist on mainnet"

    # Step 1: Warm the index
    pools_obj = await uniswap_v3.__pools__
    # Drain all pools up to the test block to ensure the index is fully populated
    pool_list = [p async for p in pools_obj.objects(to_block=V3_BLOCK)]
    assert pool_list, "Expected at least some pools to be loaded"
    print(f"Index warmed with {len(pool_list)} pools at block {V3_BLOCK}")

    # Step 2: Time individual lookups
    sample_tokens = [WETH, UNI]
    for token in sample_tokens:
        t_start = time.perf_counter()
        found = [p async for p in uniswap_v3.pools_for_token(token, V3_BLOCK)]
        elapsed_ms = (time.perf_counter() - t_start) * 1000
        print(f"  pools_for_token({token[:8]}…): {len(found)} pools in {elapsed_ms:.2f} ms")
        assert elapsed_ms < MAX_LOOKUP_MS, (
            f"pools_for_token for {token} took {elapsed_ms:.2f} ms "
            f"(threshold {MAX_LOOKUP_MS} ms). "
            "The inverted index O(1) lookup should be sub-millisecond after build."
        )
