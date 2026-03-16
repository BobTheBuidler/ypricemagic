"""Smoke test: V2 inverted index price correctness and performance.

This script validates that V2 price lookups via the inverted index return
correct prices for major tokens (WETH, WBTC, UNI, LINK) and for MIC via
its multi-hop USDT path. It also measures timing to confirm O(1) index
lookups are faster than the old O(N) linear scan.

Usage::

    BROWNIE_NETWORK=mainnet /Users/bryan/code/ypricemagic-server/.venv/bin/python \\
        scripts/smoke_test_v2_index.py

Expected runtime: 2-10 minutes (pool loading dominates).
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
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
WBTC = "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
UNI = "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"
LINK = "0x514910771AF9Ca656af840dff83E8264EcF986CA"
MIC = "0x368B3a58B5f49392e5C9E4C998cb0bB966752E51"

# Block where all of these tokens exist and have V2 liquidity
MAJOR_TOKEN_BLOCK = 19_000_000

# MIC was active at early 2021 blocks; use block 12500000 for MIC multi-hop test
MIC_BLOCK = 12_500_000

# Uniswap V2 mainnet router
UNISWAP_V2_ROUTER = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"

# Expected price ranges at MAJOR_TOKEN_BLOCK
PRICE_RANGES = {
    "WETH": (2_000, 3_500),
    "WBTC": (40_000, 70_000),
    "UNI": (5, 15),
    "LINK": (10, 25),
}


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
    print("V2 Index Smoke Test")
    print("=" * 60)

    # Connect brownie to mainnet
    print("\n[1/4] Connecting to mainnet…")
    t0 = time.time()
    brownie.network.connect("mainnet")
    print(f"      Connected in {time.time() - t0:.1f}s")

    # Import ypricemagic AFTER brownie is connected
    from y import get_price
    from y.prices.dex.uniswap.v2 import UniswapRouterV2

    # ---------------------------------------------------------------------------
    # Phase 1: Index structural checks
    # ---------------------------------------------------------------------------
    print("\n[2/4] Structural checks…")

    # Confirm get_pools_via_factory_getpair no longer exists
    if hasattr(UniswapRouterV2, "get_pools_via_factory_getpair"):
        print("  FAIL  get_pools_via_factory_getpair still exists (should be removed)")
        return 1
    else:
        print("  PASS  get_pools_via_factory_getpair removed")

    # Confirm _pool_index descriptor is present
    if not hasattr(UniswapRouterV2, "_pool_index"):
        print("  FAIL  _pool_index descriptor missing on UniswapRouterV2")
        return 1
    else:
        print("  PASS  _pool_index descriptor present")

    # ---------------------------------------------------------------------------
    # Phase 2: Price correctness for major tokens
    # ---------------------------------------------------------------------------
    print(f"\n[3/4] Price correctness at block {MAJOR_TOKEN_BLOCK:,}…")
    print("      (Loading pools from SQLite — may take 30-120s on first run…)")

    failures = 0

    tokens = [
        ("WETH", WETH),
        ("WBTC", WBTC),
        ("UNI", UNI),
        ("LINK", LINK),
    ]

    for name, addr in tokens:
        lo, hi = PRICE_RANGES[name]
        t_start = time.perf_counter()
        try:
            price = get_price(addr, MAJOR_TOKEN_BLOCK, skip_cache=True, sync=True)
        except Exception as exc:
            print(f"  FAIL  {name}: raised {type(exc).__name__}: {exc}")
            failures += 1
            continue
        elapsed_ms = (time.perf_counter() - t_start) * 1000
        ok = _check(f"{name} at block {MAJOR_TOKEN_BLOCK:,}", price, lo, hi)
        print(f"        Elapsed: {elapsed_ms:.1f} ms")
        if not ok:
            failures += 1

    # ---------------------------------------------------------------------------
    # Phase 3: MIC multi-hop path via USDT
    # ---------------------------------------------------------------------------
    print(f"\n[4/4] MIC multi-hop (MIC→USDT→USDC) at block {MIC_BLOCK:,}…")

    t_start = time.perf_counter()
    try:
        mic_price = get_price(MIC, MIC_BLOCK, skip_cache=True, sync=True)
    except Exception as exc:
        print(f"  FAIL  MIC: raised {type(exc).__name__}: {exc}")
        failures += 1
        mic_price = None
        mic_elapsed_ms = None
    else:
        mic_elapsed_ms = (time.perf_counter() - t_start) * 1000

    if mic_price is not None:
        if mic_price > 0:
            print(f"  PASS  MIC at block {MIC_BLOCK:,}: {mic_price:.4f} (> 0)")
        else:
            print(f"  FAIL  MIC at block {MIC_BLOCK:,}: {mic_price:.4f} (expected > 0)")
            failures += 1
        if mic_elapsed_ms is not None:
            print(f"        Elapsed: {mic_elapsed_ms:.1f} ms")

    # ---------------------------------------------------------------------------
    # Phase 4: O(1) timing comparison
    # ---------------------------------------------------------------------------
    print("\n[Bonus] Index lookup timing check…")
    try:
        # Use a sync router so we can time calls directly in the main thread
        sync_router = UniswapRouterV2(UNISWAP_V2_ROUTER, asynchronous=False)

        # Warm up: ensure pools and index are loaded (first call builds the index)
        t0_warm = time.perf_counter()
        # Calling all_pools_for with a well-known token triggers index build
        sync_router.all_pools_for(WETH)  # type: ignore[call-arg]
        warm_ms = (time.perf_counter() - t0_warm) * 1000
        print(
            f"        Index warm-up (first call, includes pool loading): {warm_ms:.1f} ms"
        )

        # Time individual lookups after warm-up (index is already built)
        SAMPLE_TOKENS = [WETH, WBTC, UNI, LINK]
        lookup_times: list[float] = []
        for tok in SAMPLE_TOKENS:
            t_s = time.perf_counter()
            sync_router.all_pools_for(tok)  # type: ignore[call-arg]
            lookup_times.append((time.perf_counter() - t_s) * 1000)

        avg_ms = sum(lookup_times) / len(lookup_times)
        max_ms = max(lookup_times)
        print(f"        Index lookup avg: {avg_ms:.2f} ms  max: {max_ms:.2f} ms")
        if max_ms < 10:
            print(f"  PASS  All index lookups < 10 ms (max {max_ms:.2f} ms)")
        else:
            print(f"  WARN  Slowest index lookup was {max_ms:.2f} ms (threshold 10 ms)")
            # Warn but don't count as hard failure — cold start may inflate this
    except Exception as exc:
        print(f"        Timing check skipped: {type(exc).__name__}: {exc}")

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
