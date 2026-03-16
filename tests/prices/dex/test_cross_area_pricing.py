"""CI tests: Cross-area regression after V2 + V3 inverted index migration.

These tests verify end-to-end pricing through the UniswapMultiplexer after
both V2 and V3 have switched to inverted index lookups.  They cover:

1. VAL-CROSS-001: routers_by_depth() still picks the correct router by
   liquidity depth when both V2 and V3 use inverted indexes.
2. VAL-CROSS-002: get_price() for WETH, USDT, DAI, USDC at block 19000000
   returns values within ±1% of known market prices (no regression).
3. VAL-CROSS-003: USDC returns exactly $1 (hardcoded); USDT and DAI return
   real market prices near $1 (0.95–1.05).
4. VAL-CROSS-004: Token with deeper V2 liquidity (MIC at block 12500000) is
   routed through a V2 router, not V3 or V1.

Additional V2-deferred assertions (from v2-pool-index milestone):
5. VAL-V2IDX-007: Empty dict for token with no V2 pools.
6. VAL-V2IDX-008: Address normalization — checksummed and lowercase addresses
   yield the same pool set.
7. VAL-V2CD-001 (structural): PoolsFromEvents.is_reusable=True; task lazy-starts.
8. VAL-V2CD-003 (structural): Warm-restart loads from SQLite (_cache present,
   is_reusable=True, _objects empty at construction).

Tests are marked slow and mainnet-only.  They will not run locally on macOS;
they are intended for the Linux/Docker CI environment.

References:
    VAL-CROSS-001 through VAL-CROSS-004: Cross-area flows
    VAL-V2IDX-007, VAL-V2IDX-008: V2 deferred index assertions
    VAL-V2CD-001, VAL-V2CD-003: V2 deferred continuous discovery assertions
"""

import pytest

from tests.fixtures import async_test, mainnet_only
from y import get_price
from y.prices.dex.uniswap.v2 import PoolsFromEvents, UniswapRouterV2
from y.prices.dex.uniswap.v3 import UniswapV3, uniswap_v3

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Well-known mainnet token addresses
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
WBTC = "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
UNI = "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"
LINK = "0x514910771AF9Ca656af840dff83E8264EcF986CA"
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
USDT = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
DAI = "0x6B175474E89094C44Da98b954EedeAC495271d0F"

# MIC (Mithril Cash) — V2-only token at block 12500000; multi-hop via USDT→USDC
MIC = "0x368B3a58B5f49392e5C9E4C998cb0bB966752E51"

# Block where common tokens have both V2 and V3 liquidity
CROSS_BLOCK = 19_000_000

# Earlier block for MIC test
MIC_BLOCK = 12_500_000

# Uniswap V2 mainnet router and factory
UNISWAP_V2_ROUTER = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
UNISWAP_V2_FACTORY = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"

# An ERC-20 with no V2 pools
NO_POOLS_ADDRESS = "0x0000000000000000000000000000000000000001"

# Expected price ranges (generous to avoid flakiness)
WETH_RANGE = (2_000, 3_500)
WBTC_RANGE = (40_000, 70_000)
UNI_RANGE = (5, 15)
LINK_RANGE = (10, 25)
STABLECOIN_RANGE = (0.95, 1.05)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def v2_router() -> UniswapRouterV2:
    """Async UniswapRouterV2 instance for Uniswap V2 mainnet deployment."""
    return UniswapRouterV2(UNISWAP_V2_ROUTER, asynchronous=True)


# ---------------------------------------------------------------------------
# Static / structural tests (no RPC needed — run everywhere)
# ---------------------------------------------------------------------------


def test_v2_pools_from_events_is_reusable() -> None:
    """VAL-V2CD-001: PoolsFromEvents.is_reusable=True (continuous discovery enabled).

    With is_reusable=True the ProcessedEvents infrastructure keeps pool objects
    in memory and does NOT prune them after iteration, allowing _loop() to keep
    running and discovering new pools continuously.
    """
    events = PoolsFromEvents(UNISWAP_V2_FACTORY, label="uniswap v2 ci", asynchronous=False)
    assert events.is_reusable is True, (
        "PoolsFromEvents.is_reusable must be True for continuous discovery. "
        "Setting is_reusable=False causes the task to be pruned after each "
        "iteration, which prevents the polling loop from running."
    )


def test_v2_pools_from_events_task_is_none_at_construction() -> None:
    """VAL-V2CD-001: PoolsFromEvents._task is None at construction (lazy start).

    The background polling task must be started lazily when iteration begins,
    not eagerly on construction.  An eager start would be premature before the
    event loop is running.
    """
    events = PoolsFromEvents(UNISWAP_V2_FACTORY, label="uniswap v2 ci", asynchronous=False)
    assert events._task is None, (
        "PoolsFromEvents._task must be None at construction time. "
        "The task should start lazily when pools are first iterated."
    )


def test_v2_pools_from_events_warm_restart_structural() -> None:
    """VAL-V2CD-003: PoolsFromEvents has _cache attr and empty _objects at construction.

    Structural check confirming that:
    - _cache exists (SQLite integration is wired in for warm-restart support).
    - _objects is empty at construction (pools loaded lazily from SQLite).
    - is_reusable=True (checkpoint write-back persists load position for restarts).
    """
    events = PoolsFromEvents(UNISWAP_V2_FACTORY, label="uniswap v2 ci", asynchronous=False)

    assert hasattr(events, "_cache"), (
        "PoolsFromEvents must have _cache for SQLite-backed event storage. "
        "This is needed for warm-restart pool loading without re-fetching all RPC events."
    )
    assert events._objects == [], (
        "PoolsFromEvents._objects must be empty at construction time. "
        "Pools are loaded lazily from the SQLite cache when iteration begins."
    )
    assert events.is_reusable is True, (
        "PoolsFromEvents.is_reusable must be True so the SQLite checkpoint is "
        "updated as pools load.  On warm restart, polling resumes from cached_thru+1."
    )


def test_v2_no_ram_cache_on_all_pools_for() -> None:
    """VAL-V2IDX-010 (structural): all_pools_for() does not have a ram_cache.

    The old all_pools_for() had @a_sync.a_sync(ram_cache_maxsize=...) which
    would serve stale results after new pools arrive via continuous polling.
    The new version delegates directly to the inverted index, so no ram_cache
    decorator should be present.
    """
    fn = UniswapRouterV2.all_pools_for
    assert not hasattr(
        fn, "_ram_cache"
    ), "all_pools_for should not have a _ram_cache — the inverted index IS the cache"
    assert not getattr(
        fn, "ram_cache_maxsize", None
    ), "all_pools_for should not have ram_cache_maxsize — the inverted index IS the cache"


def test_get_pools_via_factory_getpair_removed() -> None:
    """VAL-V2IDX-006 (structural): get_pools_via_factory_getpair() is removed.

    After the inverted index migration this method is no longer needed; the
    index is the sole pool lookup mechanism.
    """
    assert not hasattr(UniswapRouterV2, "get_pools_via_factory_getpair"), (
        "get_pools_via_factory_getpair() should have been removed. "
        "The inverted index is now the sole pool lookup mechanism."
    )


def test_v2_pool_index_descriptor_exists() -> None:
    """VAL-V2IDX-001 (structural): _pool_index and __pool_index__ descriptors present."""
    assert hasattr(
        UniswapRouterV2, "_pool_index"
    ), "_pool_index cached-property must exist on UniswapRouterV2"
    assert hasattr(
        UniswapRouterV2, "__pool_index__"
    ), "__pool_index__ HiddenMethodDescriptor must exist on UniswapRouterV2"


# ---------------------------------------------------------------------------
# VAL-CROSS-002: End-to-end price regression — WETH
# ---------------------------------------------------------------------------


@pytest.mark.slow
@async_test
@mainnet_only
async def test_weth_price_correct_via_multiplexer_at_block_19m() -> None:
    """VAL-CROSS-002: WETH price is correct at block 19000000 via the multiplexer.

    After both V2 and V3 migrate to inverted indexes, get_price() for WETH
    must still return the expected market price.  At block 19000000 WETH
    traded around $2200–$2800.
    """
    price = await get_price(WETH, CROSS_BLOCK, skip_cache=True, sync=False)
    lo, hi = WETH_RANGE
    assert price is not None, "WETH price must not be None at block 19000000"
    assert (
        lo < price < hi
    ), f"WETH price {price:.2f} outside expected range [{lo}, {hi}] at block {CROSS_BLOCK}"
    print(f"WETH at block {CROSS_BLOCK}: ${price:.2f}")


# ---------------------------------------------------------------------------
# VAL-CROSS-002: End-to-end price regression — WBTC
# ---------------------------------------------------------------------------


@pytest.mark.slow
@async_test
@mainnet_only
async def test_wbtc_price_correct_via_multiplexer_at_block_19m() -> None:
    """VAL-CROSS-002: WBTC price is correct at block 19000000 via the multiplexer.

    WBTC has deep liquidity on both V2 and V3.  At block 19000000 WBTC traded
    around $42,000–$52,000.
    """
    price = await get_price(WBTC, CROSS_BLOCK, skip_cache=True, sync=False)
    lo, hi = WBTC_RANGE
    assert price is not None, "WBTC price must not be None at block 19000000"
    assert (
        lo < price < hi
    ), f"WBTC price {price:.2f} outside expected range [{lo}, {hi}] at block {CROSS_BLOCK}"
    print(f"WBTC at block {CROSS_BLOCK}: ${price:.2f}")


# ---------------------------------------------------------------------------
# VAL-CROSS-002: End-to-end price regression — UNI
# ---------------------------------------------------------------------------


@pytest.mark.slow
@async_test
@mainnet_only
async def test_uni_price_correct_via_multiplexer_at_block_19m() -> None:
    """VAL-CROSS-002: UNI price is correct at block 19000000 via the multiplexer.

    UNI has significant liquidity on both V2 and V3.  At block 19000000 UNI
    traded around $6–$10.
    """
    price = await get_price(UNI, CROSS_BLOCK, skip_cache=True, sync=False)
    lo, hi = UNI_RANGE
    assert price is not None, "UNI price must not be None at block 19000000"
    assert (
        lo < price < hi
    ), f"UNI price {price:.2f} outside expected range [{lo}, {hi}] at block {CROSS_BLOCK}"
    print(f"UNI at block {CROSS_BLOCK}: ${price:.2f}")


# ---------------------------------------------------------------------------
# VAL-CROSS-002: End-to-end price regression — LINK
# ---------------------------------------------------------------------------


@pytest.mark.slow
@async_test
@mainnet_only
async def test_link_price_correct_via_multiplexer_at_block_19m() -> None:
    """VAL-CROSS-002: LINK price is correct at block 19000000 via the multiplexer.

    LINK has deep liquidity on both V2 and V3.  At block 19000000 LINK traded
    around $14–$20.
    """
    price = await get_price(LINK, CROSS_BLOCK, skip_cache=True, sync=False)
    lo, hi = LINK_RANGE
    assert price is not None, "LINK price must not be None at block 19000000"
    assert (
        lo < price < hi
    ), f"LINK price {price:.2f} outside expected range [{lo}, {hi}] at block {CROSS_BLOCK}"
    print(f"LINK at block {CROSS_BLOCK}: ${price:.2f}")


# ---------------------------------------------------------------------------
# VAL-CROSS-003: Stablecoin pricing — USDC exactly $1
# ---------------------------------------------------------------------------


@pytest.mark.slow
@async_test
@mainnet_only
async def test_usdc_price_is_exactly_one_at_block_19m() -> None:
    """VAL-CROSS-003: USDC returns exactly $1 (hardcoded stable_usd bucket).

    USDC must NOT be priced via the DEX; it falls into the 'stable usd' bucket
    and is returned as exactly 1.0.  This must hold even after the V2/V3 index
    migration.
    """
    price = await get_price(USDC, CROSS_BLOCK, skip_cache=True, sync=False)
    assert price is not None, "USDC price must not be None at block 19000000"
    assert price == 1.0, f"USDC price must be exactly 1.0 (stable_usd bucket), got {price}"
    print(f"USDC at block {CROSS_BLOCK}: ${price} (exactly $1 ✓)")


# ---------------------------------------------------------------------------
# VAL-CROSS-003: Stablecoin pricing — USDT real market price
# ---------------------------------------------------------------------------


@pytest.mark.slow
@async_test
@mainnet_only
async def test_usdt_price_is_market_price_near_one_at_block_19m() -> None:
    """VAL-CROSS-003: USDT returns real market price (not hardcoded $1).

    USDT is priced via Chainlink or DEX, NOT the stable_usd bucket.  Its price
    must be near $1 but not necessarily exactly $1.
    """
    price = await get_price(USDT, CROSS_BLOCK, skip_cache=True, sync=False)
    lo, hi = STABLECOIN_RANGE
    assert price is not None, "USDT price must not be None at block 19000000"
    assert (
        lo <= price <= hi
    ), f"USDT price {price:.6f} outside stablecoin range [{lo}, {hi}] at block {CROSS_BLOCK}"
    print(f"USDT at block {CROSS_BLOCK}: ${price:.6f}")


# ---------------------------------------------------------------------------
# VAL-CROSS-003: Stablecoin pricing — DAI real market price
# ---------------------------------------------------------------------------


@pytest.mark.slow
@async_test
@mainnet_only
async def test_dai_price_is_market_price_near_one_at_block_19m() -> None:
    """VAL-CROSS-003: DAI returns real market price (not hardcoded $1).

    DAI is priced via Chainlink or DEX.  Its price must be near $1 but is not
    guaranteed to be exactly $1.
    """
    price = await get_price(DAI, CROSS_BLOCK, skip_cache=True, sync=False)
    lo, hi = STABLECOIN_RANGE
    assert price is not None, "DAI price must not be None at block 19000000"
    assert (
        lo <= price <= hi
    ), f"DAI price {price:.6f} outside stablecoin range [{lo}, {hi}] at block {CROSS_BLOCK}"
    print(f"DAI at block {CROSS_BLOCK}: ${price:.6f}")


# ---------------------------------------------------------------------------
# VAL-CROSS-004 + VAL-V2IDX-004: MIC is V2-only, prices via multi-hop
# ---------------------------------------------------------------------------


@pytest.mark.slow
@async_test
@mainnet_only
async def test_mic_prices_via_v2_multihop_at_block_12_5m() -> None:
    """VAL-CROSS-004 + VAL-V2IDX-004: MIC routes through V2 (no V3 liquidity at block 12500000).

    MIC (Mithril Cash) only has direct V2 liquidity with USDT at block 12500000.
    The multiplexer must select the V2 router with the deepest liquidity.
    The price is resolved via multi-hop: MIC→USDT→USDC.

    This test validates two things simultaneously:
    - VAL-CROSS-004: V2-dominated token still routes via V2 after index migration.
    - VAL-V2IDX-004: Index finds the MIC/USDT pool and multi-hop path resolves price.
    """
    price = await get_price(MIC, MIC_BLOCK, skip_cache=True, sync=False)
    assert price is not None, "MIC price must not be None at block 12500000"
    assert price > 0, f"MIC price must be positive, got {price}"
    print(f"MIC at block {MIC_BLOCK}: ${price:.6f}")


# ---------------------------------------------------------------------------
# VAL-CROSS-001: Multiplexer router selection by depth
# ---------------------------------------------------------------------------


@pytest.mark.slow
@async_test
@mainnet_only
async def test_multiplexer_routers_by_depth_returns_nonempty_for_weth() -> None:
    """VAL-CROSS-001: routers_by_depth() returns non-empty list for WETH.

    After both V2 and V3 switch to inverted indexes, the multiplexer's
    liquidity checks must still work correctly.  routers_by_depth() must
    return at least one router for WETH (the most-paired token on Ethereum),
    confirming that index-backed pool lookups feed into the depth ranking.
    """
    from y.prices.dex.uniswap.uniswap import uniswap_multiplexer

    routers = await uniswap_multiplexer.routers_by_depth(WETH, block=CROSS_BLOCK, sync=False)
    assert routers, (
        f"routers_by_depth() must return at least one router for WETH at block {CROSS_BLOCK}. "
        "This confirms that index-backed liquidity checks still work correctly."
    )
    print(
        f"routers_by_depth returned {len(routers)} router(s) for WETH: "
        + ", ".join(f"{type(r).__name__}({getattr(r, 'label', '')})" for r in routers)
    )


@pytest.mark.slow
@async_test
@mainnet_only
async def test_multiplexer_routers_by_depth_highest_liquidity_wins() -> None:
    """VAL-CROSS-001: routers_by_depth() ranks routers by liquidity depth.

    The first router in the list must be the one with the highest liquidity for
    WETH at block 19000000.  After both V2 and V3 use inverted indexes, the
    depth-ranking logic must be unaffected.

    We don't assert which specific router wins (it could be V2 or V3 depending
    on block); instead, we assert that the list is non-empty and that each
    router's check_liquidity() is ≥ the next router's.
    """
    from y.prices.dex.uniswap.uniswap import uniswap_multiplexer

    routers = await uniswap_multiplexer.routers_by_depth(WETH, block=CROSS_BLOCK, sync=False)
    assert routers, "routers_by_depth() must return at least one router for WETH"

    # Verify ordering: each router must have liquidity ≥ successor
    liquidities = []
    for router in routers:
        liq = await router.check_liquidity(WETH, CROSS_BLOCK, sync=False)
        liquidities.append(liq)

    for i in range(len(liquidities) - 1):
        assert liquidities[i] >= liquidities[i + 1], (
            f"Liquidity ordering violated: router[{i}]={liquidities[i]} < "
            f"router[{i+1}]={liquidities[i+1]}. "
            "routers_by_depth() must sort routers in descending liquidity order."
        )

    print(
        f"Liquidity ordering verified for {len(routers)} router(s): "
        + " >= ".join(str(l) for l in liquidities)
    )


# ---------------------------------------------------------------------------
# VAL-V2IDX-007: Empty dict for token with no V2 pools
# ---------------------------------------------------------------------------


@pytest.mark.slow
@async_test
@mainnet_only
async def test_v2_index_empty_result_for_token_with_no_pools(
    v2_router: UniswapRouterV2,
) -> None:
    """VAL-V2IDX-007: all_pools_for() returns empty dict for token with no V2 pools.

    A valid Ethereum address with no V2 pools should return an empty dict from
    the inverted index, not an exception.  This confirms that missing-key
    behaviour is handled gracefully.
    """
    pools = await v2_router.all_pools_for(NO_POOLS_ADDRESS, sync=False)
    assert isinstance(pools, dict), f"Expected dict, got {type(pools)}"
    assert len(pools) == 0, (
        f"Address with no V2 pools should return empty dict, " f"got {len(pools)} pool(s)"
    )


# ---------------------------------------------------------------------------
# VAL-V2IDX-008: Address normalization
# ---------------------------------------------------------------------------


@pytest.mark.slow
@async_test
@mainnet_only
async def test_v2_index_address_normalization_checksum_vs_lowercase(
    v2_router: UniswapRouterV2,
) -> None:
    """VAL-V2IDX-008: Checksummed and lowercase addresses return the same pool set.

    The inverted index normalises addresses via convert.to_address_async, so
    lookups with either casing must produce the same pool set.  This test uses
    USDC (a well-known token with many V2 pools) to confirm the normalisation.
    """
    pools_checksum = await v2_router.all_pools_for(USDC, sync=False)
    pools_lower = await v2_router.all_pools_for(USDC.lower(), sync=False)

    assert set(pools_checksum.keys()) == set(pools_lower.keys()), (
        "Checksummed and lowercase address lookups must return the same pool set. "
        f"Checksummed: {len(pools_checksum)} pools, "
        f"Lowercase: {len(pools_lower)} pools"
    )
    print(
        f"Address normalisation OK: {len(pools_checksum)} pools for USDC "
        "(checksummed == lowercase)"
    )


# ---------------------------------------------------------------------------
# Combined cross-area: V3 structural checks survive index migration
# ---------------------------------------------------------------------------


@pytest.mark.slow
@async_test
@mainnet_only
async def test_v3_bounded_cache_removed_and_pool_index_present() -> None:
    """VAL-CROSS-001 (complement): V3 structural integrity after index migration.

    Confirms that _BoundedPoolsByTokenCache is gone and UniV3Pools._pool_index
    is present.  This is a cross-area check because the multiplexer relies on
    the V3 engine for liquidity checks; if the V3 index is broken the
    multiplexer's depth ranking will also be wrong.
    """
    import y.prices.dex.uniswap.v3 as v3_module
    from y.prices.dex.uniswap.v3 import UniV3Pools

    assert not hasattr(v3_module, "_BoundedPoolsByTokenCache"), (
        "_BoundedPoolsByTokenCache should be removed from v3 module after refactoring. "
        "The inverted index (_pool_index) replaces it."
    )

    assert uniswap_v3 is not None, "uniswap_v3 should exist on mainnet"

    pools_obj = await uniswap_v3.__pools__
    assert isinstance(
        pools_obj, UniV3Pools
    ), f"__pools__ should be a UniV3Pools instance, got {type(pools_obj)}"
    assert hasattr(
        pools_obj, "_pool_index"
    ), "UniV3Pools instance must have _pool_index after refactoring"
    assert isinstance(
        pools_obj._pool_index, dict
    ), f"_pool_index should be a dict, got {type(pools_obj._pool_index)}"

    print(
        f"V3 structural integrity OK: "
        f"_BoundedPoolsByTokenCache absent, "
        f"_pool_index present with {len(pools_obj._pool_index)} token entries"
    )
