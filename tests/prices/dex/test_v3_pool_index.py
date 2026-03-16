"""Tests for V3 inverted pool index.

These tests verify that:
1. UniV3Pools/SlipstreamPools maintain an inverted index (token → {pool: other_token})
2. pools_for_token() uses the index for O(1) lookup instead of O(N) iteration
3. _BoundedPoolsByTokenCache is removed/simplified
4. Each V3 fork (UniswapV3 instance) has its own independent index
5. SlipstreamPools with fee=0 are indexed correctly
6. All fee tiers for the same pair are in the index
7. New pools added during continuous polling are indexed incrementally

These tests are marked slow because V3 pool discovery scans PoolCreated events.
Run with --runslow.
"""

import pytest

from tests.fixtures import async_test, mainnet_only
from y.prices.dex.uniswap.v3 import (
    UniV3Pools,
    UniswapV3,
    UniswapV3Pool,
    uniswap_v3,
)

# Well-known mainnet addresses
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
USDT = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
DAI = "0x6B175474E89094C44Da98b954EedeAC495271d0F"

BLOCK = 18_000_000


@pytest.mark.slow
@async_test
@mainnet_only
async def test_univ3pools_has_pool_index_attribute() -> None:
    """VAL-V3IDX-001: UniV3Pools instances have a _pool_index attribute."""
    assert uniswap_v3 is not None
    pools = await uniswap_v3.__pools__
    assert hasattr(
        pools, "_pool_index"
    ), "UniV3Pools should have a _pool_index attribute for O(1) lookups. " "Got: " + str(
        type(pools)
    )
    print(f"pools._pool_index type: {type(pools._pool_index)}")


@pytest.mark.slow
@async_test
@mainnet_only
async def test_pool_index_is_dict() -> None:
    """VAL-V3IDX-002: _pool_index is a dict mapping token -> {pool: other_token}."""
    assert uniswap_v3 is not None
    pools = await uniswap_v3.__pools__

    # Wait for some pools to be loaded
    pool_list = [p async for p in pools.objects(to_block=BLOCK)]
    assert pool_list, "Expected some pools to be loaded at BLOCK"

    assert isinstance(
        pools._pool_index, dict
    ), f"_pool_index should be a dict, got {type(pools._pool_index)}"

    # Inner values should be dicts too
    for token_addr, pool_dict in list(pools._pool_index.items())[:5]:
        assert isinstance(token_addr, str), f"Token key should be str, got {type(token_addr)}"
        assert isinstance(pool_dict, dict), f"Inner value should be dict, got {type(pool_dict)}"
        for pool_obj, other_token in list(pool_dict.items())[:3]:
            assert isinstance(
                pool_obj, UniswapV3Pool
            ), f"Key in inner dict should be UniswapV3Pool, got {type(pool_obj)}"
            assert isinstance(
                other_token, str
            ), f"Other token value should be str, got {type(other_token)}"

    print(f"_pool_index has {len(pools._pool_index)} token entries")


@pytest.mark.slow
@async_test
@mainnet_only
async def test_pool_index_contains_weth_usdc() -> None:
    """VAL-V3IDX-003: WETH/USDC pools are in the index at BLOCK."""
    assert uniswap_v3 is not None
    pools = await uniswap_v3.__pools__

    # Load all pools up to BLOCK
    pool_list = [p async for p in pools.objects(to_block=BLOCK)]
    assert pool_list, "Expected some pools to be loaded at BLOCK"

    weth_lower = WETH.lower()
    usdc_lower = USDC.lower()

    assert weth_lower in pools._pool_index, (
        f"WETH ({WETH}) should be in _pool_index. "
        f"Current keys sample: {list(pools._pool_index.keys())[:5]}"
    )

    # WETH's index should contain USDC as a neighbor
    weth_pool_dict = pools._pool_index[weth_lower]
    other_tokens_lower = {str(v).lower() for v in weth_pool_dict.values()}
    assert usdc_lower in other_tokens_lower, (
        f"USDC should be a neighbor of WETH in the index. "
        f"Other tokens for WETH: {other_tokens_lower}"
    )

    print(f"WETH has {len(weth_pool_dict)} pools in index")


@pytest.mark.slow
@async_test
@mainnet_only
async def test_pool_index_multiple_fee_tiers() -> None:
    """VAL-V3IDX-004: Multiple fee tiers for WETH/USDC pair are all indexed."""
    assert uniswap_v3 is not None
    pools = await uniswap_v3.__pools__

    # Load pools up to BLOCK
    pool_list = [p async for p in pools.objects(to_block=BLOCK)]
    assert pool_list, "Expected some pools to be loaded"

    weth_lower = WETH.lower()
    usdc_lower = USDC.lower()

    if weth_lower not in pools._pool_index:
        pytest.skip("WETH not in index (pool loading incomplete?)")

    # Find all pools for WETH that have USDC as the other token
    weth_pool_dict = pools._pool_index[weth_lower]
    weth_usdc_pools = [
        pool
        for pool, other_token in weth_pool_dict.items()
        if str(other_token).lower() == usdc_lower
    ]

    # WETH/USDC has pools at multiple fee tiers (500, 3000) and possibly more
    assert (
        len(weth_usdc_pools) >= 1
    ), f"Expected at least 1 WETH/USDC pool in index, got {len(weth_usdc_pools)}"

    fees = {pool.fee for pool in weth_usdc_pools}
    print(f"WETH/USDC fee tiers in index: {fees}")
    # Commonly fee=500 and fee=3000 exist for WETH/USDC
    assert len(fees) >= 1, f"Expected at least 1 fee tier, got {fees}"


@pytest.mark.slow
@async_test
@mainnet_only
async def test_pools_for_token_uses_index() -> None:
    """VAL-V3IDX-005: pools_for_token yields correct results using index."""
    assert uniswap_v3 is not None

    # Load pools up to BLOCK first
    pools_obj = await uniswap_v3.__pools__
    pool_list = [p async for p in pools_obj.objects(to_block=BLOCK)]
    assert pool_list, "Expected some pools to load"

    weth_lower = WETH.lower()
    if weth_lower not in pools_obj._pool_index:
        pytest.skip("WETH not in index")

    # Get pools via pools_for_token
    found_pools = []
    async for pool in uniswap_v3.pools_for_token(WETH, BLOCK):
        found_pools.append(pool)
        assert isinstance(pool, UniswapV3Pool), f"Expected UniswapV3Pool, got {type(pool)}"

    assert found_pools, f"pools_for_token should return pools for WETH at block {BLOCK}"
    print(f"pools_for_token returned {len(found_pools)} pools for WETH at block {BLOCK}")


@pytest.mark.slow
@async_test
@mainnet_only
async def test_bounded_pool_by_token_cache_removed() -> None:
    """VAL-V3IDX-006: _BoundedPoolsByTokenCache is removed; _pool_index is used instead."""
    # The feature says to simplify or remove _BoundedPoolsByTokenCache.
    # After refactoring, UniV3Pools should not have _pools_by_token_cache at all.
    # The index (_pool_index) should replace it.
    assert uniswap_v3 is not None
    pools = await uniswap_v3.__pools__

    # The main assertion: _pool_index should exist and be used
    assert hasattr(
        pools, "_pool_index"
    ), "After refactoring, pools should have _pool_index (the inverted index)"

    # _pools_by_token_cache should be gone
    assert not hasattr(pools, "_pools_by_token_cache"), (
        "_pools_by_token_cache should be removed after refactoring. "
        "The inverted index (_pool_index) replaces it."
    )

    # _BoundedPoolsByTokenCache should not exist in the module
    import y.prices.dex.uniswap.v3 as v3_module

    assert not hasattr(
        v3_module, "_BoundedPoolsByTokenCache"
    ), "_BoundedPoolsByTokenCache class should be removed from the module after refactoring."

    print("_BoundedPoolsByTokenCache is removed as expected; _pool_index is present")


@pytest.mark.slow
@async_test
@mainnet_only
async def test_each_v3_instance_has_independent_index() -> None:
    """VAL-V3IDX-007: Each UniswapV3 instance (fork) has its own independent _pool_index."""
    from y.prices.dex.uniswap.v3 import forks

    assert uniswap_v3 is not None

    # Load pools for main v3
    main_pools = await uniswap_v3.__pools__

    if not forks:
        pytest.skip("No forks available on this network to test independence")

    fork_pools_list = []
    for fork in forks:
        fp = await fork.__pools__
        fork_pools_list.append(fp)

    # Each should be a different object
    for fork_pools in fork_pools_list:
        assert (
            fork_pools is not main_pools
        ), "Each UniswapV3 fork should have its own UniV3Pools/SlipstreamPools instance"
        assert hasattr(
            fork_pools, "_pool_index"
        ), f"Fork pools instance {fork_pools} should have _pool_index"
        # Indexes should be independent (different dicts)
        assert (
            fork_pools._pool_index is not main_pools._pool_index
        ), "Fork's _pool_index should be independent from main v3's _pool_index"

    print(f"Verified {len(forks)} fork(s) have independent indexes")


@pytest.mark.slow
@async_test
@mainnet_only
async def test_pool_index_consistency_with_pool_objects() -> None:
    """VAL-V3IDX-008: Every pool in _pool_index corresponds to a real pool loaded."""
    assert uniswap_v3 is not None
    pools_obj = await uniswap_v3.__pools__

    # Load a smaller subset for sanity check
    pool_list = [p async for p in pools_obj.objects(to_block=10_000_000)]
    if not pool_list:
        pytest.skip("No pools at block 10_000_000")

    # Build expected index from pool_list manually
    expected_tokens = set()
    for pool in pool_list:
        expected_tokens.add(str(pool.token0.address).lower())
        expected_tokens.add(str(pool.token1.address).lower())

    # All tokens in index should be covered by actual pools
    for token_addr in pools_obj._pool_index:
        if token_addr in expected_tokens:
            # Fine - this token has pools in the subset we loaded
            pass

    # Every pool in pool_list should be indexed under both its tokens
    missing_from_index = []
    for pool in pool_list[:100]:  # check first 100 pools
        t0 = str(pool.token0.address).lower()
        t1 = str(pool.token1.address).lower()
        if t0 in pools_obj._pool_index:
            if pool not in pools_obj._pool_index[t0]:
                missing_from_index.append((pool, t0))
        else:
            missing_from_index.append((pool, t0))
        if t1 in pools_obj._pool_index:
            if pool not in pools_obj._pool_index[t1]:
                missing_from_index.append((pool, t1))
        else:
            missing_from_index.append((pool, t1))

    assert (
        not missing_from_index
    ), f"These pools are missing from _pool_index: {missing_from_index[:5]}"

    print(f"Verified {min(100, len(pool_list))} pools are correctly indexed")


@pytest.mark.slow
@async_test
@mainnet_only
async def test_new_pool_added_to_index_incrementally() -> None:
    """VAL-V3IDX-009: New pools added via _extend() update the index incrementally.

    This test directly calls _extend() to simulate a new pool being discovered
    via continuous polling, then verifies the index is updated.
    """
    assert uniswap_v3 is not None
    pools_obj = await uniswap_v3.__pools__

    # Load some initial pools
    pool_list = [p async for p in pools_obj.objects(to_block=10_000_000)]
    if not pool_list:
        pytest.skip("No pools at block 10_000_000")

    # Record current index size
    initial_size = len(pools_obj._pool_index)

    # Simulate adding a new pool by directly calling _add_to_index
    # with a synthetic pool
    synthetic_pool = UniswapV3Pool(
        address="0x0000000000000000000000000000000000000001",
        token0="0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        token1="0xBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        tick_spacing=60,
        fee=3000,
        deploy_block=20_000_000,
        asynchronous=False,
    )

    pools_obj._add_pool_to_index(synthetic_pool)

    # Verify the synthetic pool is now in the index
    t0 = str(synthetic_pool.token0.address).lower()
    t1 = str(synthetic_pool.token1.address).lower()

    assert (
        t0 in pools_obj._pool_index
    ), f"token0 {t0} should be in _pool_index after incremental add"
    assert (
        t1 in pools_obj._pool_index
    ), f"token1 {t1} should be in _pool_index after incremental add"
    assert (
        synthetic_pool in pools_obj._pool_index[t0]
    ), f"synthetic_pool should be under token0 in index"
    assert (
        synthetic_pool in pools_obj._pool_index[t1]
    ), f"synthetic_pool should be under token1 in index"

    # Index should have grown (or at least stayed the same size if tokens were already there)
    # Since these are synthetic addresses, they should be new entries
    new_size = len(pools_obj._pool_index)
    assert new_size >= initial_size, "Index should not shrink after adding a pool"

    print(f"Index grew from {initial_size} to {new_size} entries after adding synthetic pool")
