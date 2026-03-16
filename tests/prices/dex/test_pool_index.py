"""Tests for V2 inverted pool index on UniswapRouterV2.

These tests verify:
- _pool_index cached property exists and is built from __pools__ data
- all_pools_for() returns results from the index (O(1) dict lookup)
- get_pools_via_factory_getpair() no longer exists
- Empty dict returned for tokens with no pools
- Address normalization: checksummed and lowercased addresses return same result

References:
    VAL-V2IDX-001: Index returns same pools as linear scan for WETH
    VAL-V2IDX-002: Index finds obscure tokens missed by getPair fast path
    VAL-V2IDX-007: Empty result for token with no V2 pools
    VAL-V2IDX-008: Address normalization safe
    VAL-V2IDX-010: ram_cache does not serve stale results
"""

import pytest

from tests.fixtures import async_test, mainnet_only
from y.prices.dex.uniswap.v2 import UniswapRouterV2

# Well-known mainnet addresses
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
USDT = "0xdAC17F958D2ee523a2206206994597C13D831ec7"

# MIC (Mithril Cash) - has a USDT pool but NOT a direct USDC/WETH pool
# The old get_pools_via_factory_getpair() would only check well-known pairs,
# so MIC/USDT would be missed. The inverted index finds ALL pools.
MIC_ADDRESS = "0x368B3a58B5f49392e5C9E4C998cb0bB966752E51"

# A non-existent token address that should return empty results
NO_POOLS_ADDRESS = "0x0000000000000000000000000000000000000001"

# Uniswap V2 router address (mainnet)
UNISWAP_V2_ROUTER = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"


@pytest.fixture
def uniswap_v2_router() -> UniswapRouterV2:
    """Fixture providing a UniswapRouterV2 instance for testing."""
    return UniswapRouterV2(UNISWAP_V2_ROUTER, asynchronous=True)


def test_get_pools_via_factory_getpair_removed() -> None:
    """VAL-V2IDX-006: get_pools_via_factory_getpair no longer exists.

    The method was removed since the inverted index supersedes it.
    """
    assert not hasattr(UniswapRouterV2, "get_pools_via_factory_getpair"), (
        "get_pools_via_factory_getpair() should have been removed; "
        "the inverted index is the sole pool lookup mechanism"
    )


def test_pool_index_property_exists() -> None:
    """_pool_index cached property exists on UniswapRouterV2.

    Verifies that the inverted index property is present on the class
    (even if not yet awaited).
    """
    # _pool_index is an a_sync.aka.cached_property; __pool_index__ is the
    # HiddenMethodDescriptor for it
    assert hasattr(
        UniswapRouterV2, "_pool_index"
    ), "_pool_index property must exist on UniswapRouterV2"
    assert hasattr(
        UniswapRouterV2, "__pool_index__"
    ), "__pool_index__ HiddenMethodDescriptor must exist on UniswapRouterV2"


def test_all_pools_for_no_ram_cache() -> None:
    """VAL-V2IDX-010: all_pools_for has no ram_cache (index is the cache).

    The old all_pools_for used @a_sync.a_sync(ram_cache_maxsize=...) which
    would serve stale results after new pools arrive. The new version relies
    on the index directly, so the ram_cache decorator must not be present.
    """
    fn = UniswapRouterV2.all_pools_for
    # If the function has a _cache_info or ram_cache attribute it still has
    # the old ram_cache decorator
    assert not hasattr(
        fn, "_ram_cache"
    ), "all_pools_for should not have a ram_cache — the index IS the cache"
    # Also confirm the old maxsize attribute from a_sync is gone
    assert not getattr(
        fn, "ram_cache_maxsize", None
    ), "all_pools_for should not have ram_cache_maxsize — the index IS the cache"


@pytest.mark.slow
@async_test
@mainnet_only
async def test_pool_index_returns_dict(uniswap_v2_router: UniswapRouterV2) -> None:
    """_pool_index builds a dict keyed by checksummed address strings.

    After pools are loaded (which may take a while on first run), the index
    should be a non-empty dict with checksummed address string keys.
    """
    index = await uniswap_v2_router.__pool_index__
    assert isinstance(index, dict), f"Expected dict, got {type(index)}"
    assert len(index) > 0, "Index should be non-empty after pools load"

    # Keys must be checksummed strings
    sample_key = next(iter(index))
    assert isinstance(sample_key, str), f"Index keys must be strings, got {type(sample_key)}"
    # Checksummed addresses have mixed case
    assert sample_key != sample_key.lower() or sample_key.startswith(
        "0x0"
    ), f"Index key should be a checksummed address: {sample_key}"

    print(f"Index size: {len(index)} tokens")


@pytest.mark.slow
@async_test
@mainnet_only
async def test_all_pools_for_returns_weth_pools(uniswap_v2_router: UniswapRouterV2) -> None:
    """VAL-V2IDX-001: Index returns pools for WETH.

    WETH is the most-paired token on Uniswap V2; it should appear in the index.
    """
    pools = await uniswap_v2_router.all_pools_for(WETH, sync=False)
    assert isinstance(pools, dict), f"Expected dict, got {type(pools)}"
    assert len(pools) > 0, "WETH should have pools in the index"

    print(f"Found {len(pools)} pool(s) for WETH via inverted index")


@pytest.mark.slow
@async_test
@mainnet_only
async def test_all_pools_for_empty_for_no_pools_token(
    uniswap_v2_router: UniswapRouterV2,
) -> None:
    """VAL-V2IDX-007: Empty dict returned for tokens with no V2 pools.

    A valid Ethereum address with no V2 pools should return an empty dict,
    not an exception.
    """
    pools = await uniswap_v2_router.all_pools_for(NO_POOLS_ADDRESS, sync=False)
    assert isinstance(pools, dict), f"Expected dict, got {type(pools)}"
    assert (
        len(pools) == 0
    ), f"Address with no pools should return empty dict, got {len(pools)} pool(s)"


@pytest.mark.slow
@async_test
@mainnet_only
async def test_address_normalization_checksummed_vs_lowercase(
    uniswap_v2_router: UniswapRouterV2,
) -> None:
    """VAL-V2IDX-008: Index lookup with lowercase address returns same result as checksummed.

    The index normalises addresses via convert.to_address_async, so lookups
    with either casing should produce the same pool set.
    """
    # checksummed
    pools_checksum = await uniswap_v2_router.all_pools_for(USDC, sync=False)
    # lowercase
    usdc_lower = USDC.lower()
    pools_lower = await uniswap_v2_router.all_pools_for(usdc_lower, sync=False)

    assert set(pools_checksum.keys()) == set(pools_lower.keys()), (
        "Checksummed and lowercase address lookups must return the same pool set. "
        f"Checksummed: {len(pools_checksum)} pools, Lowercase: {len(pools_lower)} pools"
    )
    print(f"Address normalisation OK: {len(pools_checksum)} pools found with both casings for USDC")


@pytest.mark.slow
@async_test
@mainnet_only
async def test_index_finds_mic_usdt_pool(uniswap_v2_router: UniswapRouterV2) -> None:
    """VAL-V2IDX-002: Index finds MIC/USDT pool (obscure token not in routing set).

    The old get_pools_via_factory_getpair() only checked well-known pairs
    (USDC, WETH, routing tokens) so it would have missed MIC/USDT.
    The inverted index is built from ALL pools, so it finds MIC/USDT directly.
    """
    pools = await uniswap_v2_router.all_pools_for(MIC_ADDRESS, sync=False)

    assert len(pools) > 0, (
        f"Expected to find pool(s) for MIC ({MIC_ADDRESS}) in the index. "
        "MIC/USDT pool should be indexed."
    )

    # The paired tokens should include USDT
    paired_tokens_lower = {str(v).lower() for v in pools.values()}
    assert USDT.lower() in paired_tokens_lower, (
        f"Expected MIC to be paired with USDT in the index. "
        f"Found paired tokens: {paired_tokens_lower}"
    )

    print(
        f"Found {len(pools)} pool(s) for MIC via inverted index — "
        f"paired tokens: {paired_tokens_lower}"
    )


@pytest.mark.slow
@async_test
@mainnet_only
async def test_get_pools_for_uses_index_on_mainnet(uniswap_v2_router: UniswapRouterV2) -> None:
    """VAL-V2IDX-006: get_pools_for() uses the index as sole lookup on Mainnet.

    On Mainnet _supports_factory_helper is False, so get_pools_for() must fall
    through to the index-based all_pools_for() call.
    """
    assert (
        uniswap_v2_router._supports_factory_helper is False
    ), "On mainnet _supports_factory_helper should be False"

    # MIC is a good probe: old fast path missed it; index-based lookup finds it
    pools = await uniswap_v2_router.get_pools_for(MIC_ADDRESS, sync=False)
    assert isinstance(pools, dict), f"Expected dict, got {type(pools)}"
    assert len(pools) > 0, "get_pools_for should find MIC pools on mainnet via index lookup"

    paired_tokens_lower = {str(v).lower() for v in pools.values()}
    assert (
        USDT.lower() in paired_tokens_lower
    ), f"Expected MIC to be paired with USDT. Found: {paired_tokens_lower}"
    print(f"get_pools_for found {len(pools)} pool(s) for MIC via index on mainnet")
