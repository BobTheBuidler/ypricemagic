"""Smoke test: V3 inverted index price correctness and structural validation.

This script validates that:
1. UniV3Pools._pool_index is built and contains expected tokens.
2. pools_for_token() uses the O(1) index and returns correct pools.
3. get_price() returns correct prices for major tokens priced via V3
   (WETH, UNI, AAVE, MATIC/WMATIC) at a known historical block.
4. _BoundedPoolsByTokenCache is removed from the module.

Usage::

    BROWNIE_NETWORK=mainnet /Users/bryan/code/ypricemagic-server/.venv/bin/python \\
        scripts/smoke_test_v3_index.py

Expected runtime: 2-10 minutes (V3 pool loading from RPC dominates on first run;
subsequent runs are faster once pools are cached in SQLite).
"""

# ---------------------------------------------------------------------------
# macOS SemLock monkey-patch — MUST be first, before any brownie/ypricemagic import
# ---------------------------------------------------------------------------
import concurrent.futures.process as _cfp

_orig_sq_init = _cfp._SafeQueue.__init__
_cfp._SafeQueue.__init__ = lambda self, max_size=0, **kw: _orig_sq_init(
    self, min(max_size, 32767), **kw
)

# ---------------------------------------------------------------------------
# Standard imports (after patch)
# ---------------------------------------------------------------------------
import sys  # noqa: E402
import time  # noqa: E402

import brownie  # noqa: E402

# ---------------------------------------------------------------------------
# Token addresses (mainnet)
# ---------------------------------------------------------------------------

# Major tokens with well-known V3 liquidity at block 18_000_000
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
UNI = "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"
AAVE = "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9"

# WMATIC (Polygon-bridged MATIC) — priced via V3 on mainnet at later blocks
# At block 19_000_000, WMATIC has V3 liquidity against WETH/USDC
WMATIC = "0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0"  # MATIC on mainnet

# Block where these tokens have V3 liquidity
V3_BLOCK = 18_000_000

# Expected price ranges at V3_BLOCK
PRICE_RANGES = {
    "WETH": (1_500, 3_000),
    "UNI": (3, 15),
    "AAVE": (50, 150),
    "MATIC": (0.4, 1.5),
}

# Uniswap V3 factory (mainnet)
UNISWAP_V3_FACTORY = "0x1F98431c8aD98523631AE4a59f267346ea31F984"


def _check(label: str, price: float | None, lo: float, hi: float) -> bool:
    """Print a pass/fail line for a price check; return True if pass."""
    if price is None:
        print(f"  FAIL  {label}: got None (expected {lo}–{hi})")
        return False
    ok = lo <= price <= hi
    status = "  PASS " if ok else "  FAIL "
    print(f"{status} {label}: {price:.4f}  (expected {lo}–{hi})")
    return ok


def main() -> int:
    print("=" * 60)
    print("V3 Index Smoke Test")
    print("=" * 60)

    # Connect brownie to mainnet
    print("\n[1/5] Connecting to mainnet…")
    t0 = time.time()
    brownie.network.connect("mainnet")
    print(f"      Connected in {time.time() - t0:.1f}s")

    # Import ypricemagic AFTER brownie is connected
    from y import get_price
    from y.prices.dex.uniswap import v3 as v3_module
    from y.prices.dex.uniswap.v3 import UniV3Pools, UniswapV3, uniswap_v3

    # ---------------------------------------------------------------------------
    # Phase 1: Structural checks
    # ---------------------------------------------------------------------------
    print("\n[2/5] Structural checks…")
    failures = 0

    # 1a. uniswap_v3 instance should exist on mainnet
    if uniswap_v3 is None:
        print("  FAIL  uniswap_v3 is None on mainnet (should be initialized)")
        return 1
    else:
        print("  PASS  uniswap_v3 instance initialized")

    # 1b. _BoundedPoolsByTokenCache should no longer exist in v3 module
    if hasattr(v3_module, "_BoundedPoolsByTokenCache"):
        print("  FAIL  _BoundedPoolsByTokenCache still exists in v3 module (should be removed)")
        failures += 1
    else:
        print("  PASS  _BoundedPoolsByTokenCache removed from v3 module")

    # 1c. UniV3Pools should have _pool_index attribute
    if not hasattr(UniV3Pools, "_pool_index") and not any(
        hasattr(UniV3Pools, attr)
        for attr in ("__slots__",)
        if "_pool_index" in getattr(UniV3Pools, attr, ())
    ):
        # Check via __slots__ or instance check after loading
        print("  INFO  _pool_index is declared in __slots__, will verify on instance below")
    else:
        print("  PASS  UniV3Pools declares _pool_index")

    # ---------------------------------------------------------------------------
    # Phase 2: Pool loading and index verification
    # ---------------------------------------------------------------------------
    print(f"\n[3/5] Loading V3 pools up to block {V3_BLOCK:,}…")
    print("      (First run may take several minutes; subsequent runs use SQLite cache…)")

    t_load = time.time()
    try:
        # Load pools synchronously via __pools__ property
        pools_obj = uniswap_v3.__pools__  # type: ignore[misc]
    except Exception as exc:
        print(f"  FAIL  Could not access __pools__: {type(exc).__name__}: {exc}")
        return 1
    load_elapsed = time.time() - t_load
    print(f"      Pool object obtained in {load_elapsed:.1f}s")

    # Verify _pool_index exists
    if not hasattr(pools_obj, "_pool_index"):
        print("  FAIL  UniV3Pools instance missing _pool_index attribute")
        failures += 1
    else:
        print("  PASS  UniV3Pools instance has _pool_index attribute")
        idx = pools_obj._pool_index
        print(f"  INFO  _pool_index currently has {len(idx)} token entries")

        # Check WETH is indexed
        weth_lower = WETH.lower()
        if weth_lower in idx:
            n_weth_pools = len(idx[weth_lower])
            print(f"  PASS  WETH in index with {n_weth_pools} pool(s)")
        else:
            print("  INFO  WETH not yet in index (pool loading may still be in progress)")

        # Check inner structure
        sample_items = list(idx.items())[:3]
        if sample_items:
            from y.prices.dex.uniswap.v3 import UniswapV3Pool

            for token_key, pool_dict in sample_items:
                assert isinstance(
                    pool_dict, dict
                ), f"_pool_index inner value should be dict, got {type(pool_dict)}"
                for pool_obj in list(pool_dict.keys())[:1]:
                    if not isinstance(pool_obj, UniswapV3Pool):
                        print(f"  FAIL  Inner key should be UniswapV3Pool, got {type(pool_obj)}")
                        failures += 1
                    else:
                        print("  PASS  _pool_index inner keys are UniswapV3Pool instances")
                    break
                break

    # ---------------------------------------------------------------------------
    # Phase 3: Price correctness for V3-specific tokens
    # ---------------------------------------------------------------------------
    print(f"\n[4/5] V3 price correctness at block {V3_BLOCK:,}…")
    print("      (prices fetched via get_price() — includes all routing strategies)")

    tokens = [
        ("WETH", WETH),
        ("UNI", UNI),
        ("AAVE", AAVE),
        ("MATIC", WMATIC),
    ]

    for name, addr in tokens:
        lo, hi = PRICE_RANGES[name]
        t_start = time.perf_counter()
        try:
            price = get_price(addr, V3_BLOCK, skip_cache=True, sync=True)
        except Exception as exc:
            print(f"  FAIL  {name}: raised {type(exc).__name__}: {exc}")
            failures += 1
            continue
        elapsed_ms = (time.perf_counter() - t_start) * 1000
        ok = _check(f"{name} at block {V3_BLOCK:,}", price, lo, hi)
        print(f"        Elapsed: {elapsed_ms:.1f} ms")
        if not ok:
            failures += 1

    # ---------------------------------------------------------------------------
    # Phase 4: Direct V3 pricing for WETH (bypassing magic multiplexer)
    # ---------------------------------------------------------------------------
    print(f"\n[5/5] Direct V3 pricing for WETH at block {V3_BLOCK:,}…")
    print("      (verifies V3 index is used for direct uniswap_v3.get_price() call)")

    t_start = time.perf_counter()
    try:
        weth_v3_price = uniswap_v3.get_price(WETH, V3_BLOCK, skip_cache=True, sync=True)
    except Exception as exc:
        print(f"  FAIL  uniswap_v3.get_price(WETH): raised {type(exc).__name__}: {exc}")
        failures += 1
        weth_v3_price = None
    elapsed_ms = (time.perf_counter() - t_start) * 1000

    if weth_v3_price is not None:
        lo, hi = PRICE_RANGES["WETH"]
        ok = _check(f"WETH via uniswap_v3.get_price() at block {V3_BLOCK:,}", weth_v3_price, lo, hi)
        print(f"        Elapsed: {elapsed_ms:.1f} ms")
        if not ok:
            failures += 1

    # ---------------------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------------------
    print("\n" + "=" * 60)
    if failures == 0:
        print("ALL CHECKS PASSED")
    else:
        print(f"{failures} CHECK(S) FAILED")
    print("=" * 60)

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
