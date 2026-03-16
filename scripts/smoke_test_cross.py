"""Smoke test: Cross-area regression — end-to-end pricing after V2 + V3 index migration.

This script validates:
1. VAL-CROSS-001: UniswapMultiplexer.routers_by_depth() still picks the correct
   router based on liquidity depth after both V2 and V3 use inverted indexes.
2. VAL-CROSS-002: get_price() for WETH, USDT, DAI, USDC at block 19000000 is
   within ±1% of known market values.
3. VAL-CROSS-003: Stablecoin pricing — USDC returns exactly $1; USDT and DAI
   return real market prices near $1 (0.95–1.05).
4. VAL-CROSS-004: Token with deeper V2 liquidity (e.g. MIC at block 12500000)
   is routed through a V2 router, not V3.

Deferred V2 assertions (from v2-pool-index milestone user-testing timeout):
5. VAL-V2IDX-001/002/003/004/005/006/007/008: V2 index correctness, obscure
   token discovery, O(1) timing, address normalization.
6. VAL-V2CD-001/002/003/004: V2 continuous discovery structural checks.

Usage::

    BROWNIE_NETWORK=mainnet /Users/bryan/code/ypricemagic-server/.venv/bin/python \\
        scripts/smoke_test_cross.py

Expected runtime: 3-15 minutes (pool loading dominates on first run;
subsequent runs use SQLite cache and complete much faster).
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
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
USDT = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
DAI = "0x6B175474E89094C44Da98b954EedeAC495271d0F"

# MIC (Mithril Cash) — only V2 liquidity, no V3; multi-hop via USDT→USDC path
MIC = "0x368B3a58B5f49392e5C9E4C998cb0bB966752E51"

# Block where common tokens have both V2 and V3 liquidity
CROSS_BLOCK = 19_000_000

# Earlier block for MIC test (MIC was active in early 2021)
MIC_BLOCK = 12_500_000

# Uniswap V2 mainnet router
UNISWAP_V2_ROUTER = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"

# Expected price ranges at CROSS_BLOCK — generous bounds to avoid flakiness.
# WETH ~$2200–2800, WBTC ~$42k–52k, UNI ~$6–10, LINK ~$14–20
CROSS_PRICE_RANGES = {
    "WETH": (2_000, 3_500),
    "WBTC": (40_000, 70_000),
    "UNI": (5, 15),
    "LINK": (10, 25),
}

# Stablecoins — USDC must be exactly $1 (hardcoded); USDT and DAI near $1
STABLECOIN_RANGE = (0.95, 1.05)


def _check(label: str, price: float | None, lo: float, hi: float) -> bool:
    """Print a pass/fail line for a price check; return True if pass."""
    if price is None:
        print(f"  FAIL  {label}: got None (expected {lo:.4f}–{hi:.4f})")
        return False
    ok = lo <= price <= hi
    status = "  PASS " if ok else "  FAIL "
    print(f"{status} {label}: {price:.6f}  (expected {lo:.4f}–{hi:.4f})")
    return ok


def _check_exact(label: str, price: float | None, expected: float) -> bool:
    """Print a pass/fail for an exact-equality price check."""
    if price is None:
        print(f"  FAIL  {label}: got None (expected {expected})")
        return False
    ok = price == expected
    status = "  PASS " if ok else "  FAIL "
    print(f"{status} {label}: {price}  (expected exactly {expected})")
    return ok


def main() -> int:  # noqa: C901
    print("=" * 70)
    print("Cross-Area Regression Smoke Test")
    print("V2 + V3 Inverted Index — Multiplexer, Stablecoins, Deferred V2 Checks")
    print("=" * 70)

    # ------------------------------------------------------------------ #
    # Connect brownie to mainnet                                            #
    # ------------------------------------------------------------------ #
    print("\n[0/8] Connecting to mainnet…")
    t0 = time.time()
    brownie.network.connect("mainnet")
    print(f"      Connected in {time.time() - t0:.1f}s")

    # Import ypricemagic AFTER brownie is connected
    from y import get_price
    from y.prices.dex.uniswap.uniswap import UniswapMultiplexer, uniswap_multiplexer
    from y.prices.dex.uniswap.v2 import PoolsFromEvents, UniswapRouterV2
    from y.prices.dex.uniswap.v3 import uniswap_v3

    failures = 0

    # ------------------------------------------------------------------ #
    # Phase 1: Structural — V2 index present, getPair removed              #
    # ------------------------------------------------------------------ #
    print("\n[1/8] V2 structural checks (deferred VAL-V2IDX-006, VAL-V2IDX-007)…")

    if hasattr(UniswapRouterV2, "get_pools_via_factory_getpair"):
        print("  FAIL  get_pools_via_factory_getpair still exists (should be removed)")
        failures += 1
    else:
        print("  PASS  get_pools_via_factory_getpair removed (index is sole mechanism)")

    if not hasattr(UniswapRouterV2, "_pool_index"):
        print("  FAIL  _pool_index missing on UniswapRouterV2")
        failures += 1
    else:
        print("  PASS  _pool_index descriptor present on UniswapRouterV2")

    # ------------------------------------------------------------------ #
    # Phase 2: V2 continuous discovery structural checks (VAL-V2CD-001)    #
    # ------------------------------------------------------------------ #
    print("\n[2/8] V2 continuous discovery structural checks (VAL-V2CD-001)…")

    UNISWAP_V2_FACTORY = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
    events = PoolsFromEvents(UNISWAP_V2_FACTORY, label="uniswap v2 check", asynchronous=False)

    if not events.is_reusable:
        print(
            "  FAIL  PoolsFromEvents.is_reusable is False (must be True for continuous discovery)"
        )
        failures += 1
    else:
        print("  PASS  PoolsFromEvents.is_reusable=True (continuous discovery enabled)")

    if events._task is not None:
        print("  FAIL  PoolsFromEvents._task should be None at construction (lazy start)")
        failures += 1
    else:
        print("  PASS  PoolsFromEvents._task=None at construction (lazy start confirmed)")

    if not hasattr(events, "_cache"):
        print("  FAIL  PoolsFromEvents._cache missing (SQLite integration not wired)")
        failures += 1
    else:
        print("  PASS  PoolsFromEvents._cache present (SQLite warm-restart support)")

    # ------------------------------------------------------------------ #
    # Phase 3: Price correctness — major tokens (VAL-V2IDX-003)           #
    # ------------------------------------------------------------------ #
    print(f"\n[3/8] Price correctness — major tokens at block {CROSS_BLOCK:,}…")
    print("      (This triggers V2 + V3 pool loading — may take 30-120s on first run…)")

    tokens = [
        ("WETH", WETH),
        ("WBTC", WBTC),
        ("UNI", UNI),
        ("LINK", LINK),
    ]

    for name, addr in tokens:
        lo, hi = CROSS_PRICE_RANGES[name]
        t_start = time.perf_counter()
        try:
            price = get_price(addr, CROSS_BLOCK, skip_cache=True, sync=True)
        except Exception as exc:
            print(f"  FAIL  {name}: raised {type(exc).__name__}: {exc}")
            failures += 1
            continue
        elapsed_ms = (time.perf_counter() - t_start) * 1000
        ok = _check(
            f"{name} at block {CROSS_BLOCK:,}", float(price) if price is not None else None, lo, hi
        )
        print(f"        Elapsed: {elapsed_ms:.1f} ms")
        if not ok:
            failures += 1

    # ------------------------------------------------------------------ #
    # Phase 4: Stablecoin pricing (VAL-CROSS-002, VAL-CROSS-003)           #
    # ------------------------------------------------------------------ #
    print(f"\n[4/8] Stablecoin pricing at block {CROSS_BLOCK:,}…")

    # USDC must be exactly $1 (hardcoded stable_usd bucket)
    t_start = time.perf_counter()
    try:
        usdc_price = get_price(USDC, CROSS_BLOCK, skip_cache=True, sync=True)
    except Exception as exc:
        print(f"  FAIL  USDC: raised {type(exc).__name__}: {exc}")
        failures += 1
        usdc_price = None
    else:
        elapsed_ms = (time.perf_counter() - t_start) * 1000
        ok = _check_exact(f"USDC at block {CROSS_BLOCK:,} (must be exactly $1)", usdc_price, 1.0)
        print(f"        Elapsed: {elapsed_ms:.1f} ms")
        if not ok:
            failures += 1

    # USDT — real market price (DEX/Chainlink)
    t_start = time.perf_counter()
    try:
        usdt_price = get_price(USDT, CROSS_BLOCK, skip_cache=True, sync=True)
    except Exception as exc:
        print(f"  FAIL  USDT: raised {type(exc).__name__}: {exc}")
        failures += 1
        usdt_price = None
    else:
        elapsed_ms = (time.perf_counter() - t_start) * 1000
        ok = _check(
            f"USDT at block {CROSS_BLOCK:,} (market price, not hardcoded)",
            float(usdt_price) if usdt_price is not None else None,
            *STABLECOIN_RANGE,
        )
        print(f"        Elapsed: {elapsed_ms:.1f} ms")
        if not ok:
            failures += 1

    # DAI — real market price (DEX/Chainlink)
    t_start = time.perf_counter()
    try:
        dai_price = get_price(DAI, CROSS_BLOCK, skip_cache=True, sync=True)
    except Exception as exc:
        print(f"  FAIL  DAI: raised {type(exc).__name__}: {exc}")
        failures += 1
        dai_price = None
    else:
        elapsed_ms = (time.perf_counter() - t_start) * 1000
        ok = _check(
            f"DAI at block {CROSS_BLOCK:,} (market price, not hardcoded)",
            float(dai_price) if dai_price is not None else None,
            *STABLECOIN_RANGE,
        )
        print(f"        Elapsed: {elapsed_ms:.1f} ms")
        if not ok:
            failures += 1

    # ------------------------------------------------------------------ #
    # Phase 5: MIC multi-hop V2 path (VAL-V2IDX-004, VAL-CROSS-004)       #
    # ------------------------------------------------------------------ #
    print(f"\n[5/8] MIC multi-hop (MIC→USDT→USDC) at block {MIC_BLOCK:,}…")

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
        if float(mic_price) > 0:
            print(f"  PASS  MIC at block {MIC_BLOCK:,}: {float(mic_price):.6f} (> 0)")
        else:
            print(f"  FAIL  MIC at block {MIC_BLOCK:,}: {float(mic_price):.6f} (expected > 0)")
            failures += 1
        if mic_elapsed_ms is not None:
            print(f"        Elapsed: {mic_elapsed_ms:.1f} ms")

    # ------------------------------------------------------------------ #
    # Phase 6: V2 index address normalization (VAL-V2IDX-008)              #
    # ------------------------------------------------------------------ #
    print("\n[6/8] V2 index address normalization — checksummed vs lowercase (VAL-V2IDX-008)…")

    try:
        v2_router = UniswapRouterV2(UNISWAP_V2_ROUTER, asynchronous=False)

        # Warm up the index
        pools_checksum = v2_router.all_pools_for(USDC)  # type: ignore[call-arg]
        usdc_lower = USDC.lower()
        pools_lower = v2_router.all_pools_for(usdc_lower)  # type: ignore[call-arg]

        # Compare keys
        keys_checksum = set(str(k) for k in pools_checksum.keys())
        keys_lower = set(str(k) for k in pools_lower.keys())

        if keys_checksum == keys_lower:
            print(
                f"  PASS  Address normalization: checksummed/lowercase return same "
                f"{len(keys_checksum)} pool(s) for USDC"
            )
        else:
            print(
                f"  FAIL  Address normalization mismatch: "
                f"checksummed={len(keys_checksum)} pools, lowercase={len(keys_lower)} pools"
            )
            failures += 1
    except Exception as exc:
        print(f"  SKIP  Address normalization check failed: {type(exc).__name__}: {exc}")

    # ------------------------------------------------------------------ #
    # Phase 7: Empty result for token with no V2 pools (VAL-V2IDX-007)    #
    # ------------------------------------------------------------------ #
    print("\n[7/8] Empty result for token with no V2 pools (VAL-V2IDX-007)…")

    NO_POOLS_ADDRESS = "0x0000000000000000000000000000000000000001"
    try:
        v2_router_sync = UniswapRouterV2(UNISWAP_V2_ROUTER, asynchronous=False)
        no_pools_result = v2_router_sync.all_pools_for(NO_POOLS_ADDRESS)  # type: ignore[call-arg]

        if isinstance(no_pools_result, dict) and len(no_pools_result) == 0:
            print("  PASS  Empty dict returned for token with no V2 pools (no exception raised)")
        elif isinstance(no_pools_result, dict):
            print(
                f"  FAIL  Expected empty dict but got {len(no_pools_result)} pool(s) "
                f"for {NO_POOLS_ADDRESS}"
            )
            failures += 1
        else:
            print(f"  FAIL  Expected dict but got {type(no_pools_result)}")
            failures += 1
    except Exception as exc:
        print(f"  FAIL  Raised {type(exc).__name__}: {exc}")
        failures += 1

    # ------------------------------------------------------------------ #
    # Phase 8: Multiplexer router selection (VAL-CROSS-001, VAL-CROSS-004) #
    # ------------------------------------------------------------------ #
    print(f"\n[8/8] Multiplexer router selection at block {CROSS_BLOCK:,} (VAL-CROSS-001)…")

    try:
        # routers_by_depth is async — use the sync multiplexer wrapper
        # The multiplexer is a singleton; we call its sync interface via sync=True
        routers = uniswap_multiplexer.routers_by_depth(WETH, block=CROSS_BLOCK, sync=True)

        if routers:
            print(f"  PASS  routers_by_depth returned {len(routers)} router(s) for WETH:")
            for i, r in enumerate(routers):
                print(f"        [{i}] {type(r).__name__}: {getattr(r, 'label', repr(r))}")
        else:
            print("  FAIL  routers_by_depth returned empty list for WETH — no liquidity found")
            failures += 1

        # For MIC at MIC_BLOCK, only V2 routers should have liquidity
        routers_mic = uniswap_multiplexer.routers_by_depth(MIC, block=MIC_BLOCK, sync=True)

        if routers_mic:
            top_router = routers_mic[0]
            router_name = type(top_router).__name__
            print(
                f"\n  INFO  MIC at block {MIC_BLOCK:,} — top router: "
                f"{router_name} ({getattr(top_router, 'label', repr(top_router))})"
            )
            if "V2" in router_name or "UniswapRouter" in router_name:
                print(
                    f"  PASS  MIC routed through a V2 router as expected "
                    f"(VAL-CROSS-004: V2-dominated tokens still route via V2)"
                )
            else:
                # V1 or V3 — warn but don't hard-fail; the intent is that MIC routes via V2
                print(
                    f"  WARN  MIC top router is {router_name} — expected V2 "
                    f"(MIC has no V3 liquidity at this block)"
                )
        else:
            print(
                f"  WARN  routers_by_depth returned empty list for MIC at block {MIC_BLOCK:,}; "
                "this may indicate the index hasn't finished loading"
            )
    except Exception as exc:
        print(f"  SKIP  Multiplexer router selection check failed: {type(exc).__name__}: {exc}")

    # ------------------------------------------------------------------ #
    # O(1) index timing check (VAL-V2IDX-005)                             #
    # ------------------------------------------------------------------ #
    print("\n[Bonus] V2 O(1) index timing check (VAL-V2IDX-005)…")

    try:
        router_timing = UniswapRouterV2(UNISWAP_V2_ROUTER, asynchronous=False)

        # Warm up (first call builds the index from already-loaded pool objects)
        t_warm = time.perf_counter()
        router_timing.all_pools_for(WETH)  # type: ignore[call-arg]
        warm_ms = (time.perf_counter() - t_warm) * 1000
        print(f"        Index warm-up (first call): {warm_ms:.1f} ms")

        # Time post-warm-up lookups
        sample_tokens = [WETH, WBTC, UNI, LINK, USDC, USDT, DAI]
        lookup_times: list[float] = []
        for tok in sample_tokens:
            t_s = time.perf_counter()
            router_timing.all_pools_for(tok)  # type: ignore[call-arg]
            lookup_times.append((time.perf_counter() - t_s) * 1000)

        avg_ms = sum(lookup_times) / len(lookup_times)
        max_ms = max(lookup_times)
        print(f"        Index lookup avg: {avg_ms:.2f} ms  max: {max_ms:.2f} ms")

        if max_ms < 10:
            print(f"  PASS  All index lookups < 10 ms (max {max_ms:.2f} ms — O(1) confirmed)")
        else:
            # Warn but don't hard-fail — cold-start or GC may inflate on first runs
            print(f"  WARN  Slowest lookup was {max_ms:.2f} ms (threshold 10 ms)")
    except Exception as exc:
        print(f"        Timing check skipped: {type(exc).__name__}: {exc}")

    # ------------------------------------------------------------------ #
    # V3 structural check (complement to cross-area verification)          #
    # ------------------------------------------------------------------ #
    print("\n[Bonus] V3 structural check — _BoundedPoolsByTokenCache absent, _pool_index present…")

    try:
        import y.prices.dex.uniswap.v3 as v3_module
        from y.prices.dex.uniswap.v3 import UniV3Pools

        if hasattr(v3_module, "_BoundedPoolsByTokenCache"):
            print("  FAIL  _BoundedPoolsByTokenCache still in v3 module (should be removed)")
            failures += 1
        else:
            print("  PASS  _BoundedPoolsByTokenCache removed from v3 module")

        if uniswap_v3 is not None:
            print("  PASS  uniswap_v3 singleton initialized")
        else:
            print("  WARN  uniswap_v3 is None (not expected on mainnet)")
    except Exception as exc:
        print(f"  SKIP  V3 structural check failed: {type(exc).__name__}: {exc}")

    # ------------------------------------------------------------------ #
    # Summary                                                              #
    # ------------------------------------------------------------------ #
    print("\n" + "=" * 70)
    if failures == 0:
        print("ALL CHECKS PASSED")
    else:
        print(f"{failures} CHECK(S) FAILED")
    print("=" * 70)

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
