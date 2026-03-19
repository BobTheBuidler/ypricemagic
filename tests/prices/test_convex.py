"""Tests for Convex LP token detection and pricing.

Convex LP tokens wrap Curve LP tokens deposited in the Convex Finance booster.
Detection works in two stages:

1. **Static mapping** – hardcoded ``MAPPING`` of known tokens (fast path).
2. **Dynamic detection** – ``operator()`` → booster verification → ``poolInfo``
   iteration to find the underlying Curve LP.

This test file covers both paths.
"""

import pytest

from tests.fixtures import mainnet_only
from y.datatypes import PriceResult
from y.prices import convex, magic
from y.prices.utils.buckets import check_bucket

# ─────────────────────────────────────────────────────────────────────────────
# Token addresses
# ─────────────────────────────────────────────────────────────────────────────

# cvx3crv — IN the hardcoded MAPPING → tests the fast (static) path
CVX3CRV = "0x30D9410ED1D5DA1F6C8391af5338C93ab8d4035C"
CVX3CRV_UNDERLYING = "0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490"  # 3crv

# cvxsteCRV — NOT in the hardcoded MAPPING → tests dynamic detection
# This is the Convex deposit token for the stETH/ETH Curve pool.
CVXSTECRV = "0x9518c9063eB0262d791f38d8d6Eb0aca33c63ed0"
STECRV_LP = "0x06325440D014e39736583c165C2963BA99fAf14E"  # steCRV LP

# DAI — definitely NOT a Convex LP token (sanity check).
DAI = "0x6B175474E89094C44Da98b954EedeAC495271d0F"

# Block numbers where these tokens were deployed and active
TEST_BLOCK = 15_000_000
TEST_BLOCK_3CRV = 14_000_000


# ─────────────────────────────────────────────────────────────────────────────
# Detection tests
# ─────────────────────────────────────────────────────────────────────────────


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_hardcoded_token_is_convex():
    """A token in the hardcoded MAPPING should be detected as 'convex'."""
    bucket = await check_bucket(CVX3CRV, sync=False)
    assert bucket == "convex", (
        f"Expected 'convex' bucket for {CVX3CRV}, got '{bucket}'"
    )


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_dynamic_token_is_convex():
    """A Convex token NOT in the hardcoded MAPPING should be detected dynamically."""
    result = await convex.is_convex_lp(CVXSTECRV, sync=False)
    assert result is True, (
        f"cvxsteCRV {CVXSTECRV} should be detected as a Convex LP token"
    )


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_dynamic_token_bucket():
    """A dynamically detected Convex token should be bucketed as 'convex'."""
    bucket = await check_bucket(CVXSTECRV, sync=False)
    assert bucket == "convex", (
        f"Expected 'convex' bucket for cvxsteCRV {CVXSTECRV}, got '{bucket}'"
    )


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_non_convex_not_detected():
    """A non-Convex token (DAI) should NOT be detected as Convex."""
    result = await convex.is_convex_lp(DAI, sync=False)
    assert result is False, (
        f"DAI should not be detected as a Convex LP token"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Underlying LP resolution tests
# ─────────────────────────────────────────────────────────────────────────────


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_hardcoded_underlying_lp():
    """A hardcoded token should resolve its underlying LP from the static MAPPING."""
    lp = await convex.get_underlying_lp(CVX3CRV, sync=False)
    assert lp is not None, "get_underlying_lp should return an address for hardcoded tokens"
    assert lp.lower() == CVX3CRV_UNDERLYING.lower(), (
        f"Expected underlying LP {CVX3CRV_UNDERLYING}, got {lp}"
    )


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_dynamic_underlying_lp():
    """A dynamically detected token should resolve its underlying Curve LP."""
    lp = await convex.get_underlying_lp(CVXSTECRV, sync=False)
    assert lp is not None, (
        f"get_underlying_lp should return an address for cvxsteCRV {CVXSTECRV}"
    )
    assert lp.lower() == STECRV_LP.lower(), (
        f"Expected underlying LP {STECRV_LP}, got {lp}"
    )


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_non_convex_underlying_lp_is_none():
    """A non-Convex token should return None from get_underlying_lp."""
    lp = await convex.get_underlying_lp(DAI, sync=False)
    assert lp is None, (
        f"DAI should not have an underlying LP, got {lp}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Pricing tests
# ─────────────────────────────────────────────────────────────────────────────


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_hardcoded_convex_price():
    """A hardcoded Convex token should resolve to a non-None price."""
    result = await magic.get_price(
        CVX3CRV, TEST_BLOCK_3CRV, fail_to_None=True, skip_cache=True, sync=False
    )
    assert result is not None, (
        f"cvx3crv {CVX3CRV} should resolve to a non-None price"
    )

    price = float(result.price if isinstance(result, PriceResult) else result)
    assert price > 0, f"cvx3crv price should be positive, got {price}"


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_dynamic_convex_price():
    """A dynamically detected Convex token should resolve to a non-None price."""
    result = await magic.get_price(
        CVXSTECRV, TEST_BLOCK, fail_to_None=True, skip_cache=True, sync=False
    )
    assert result is not None, (
        f"cvxsteCRV {CVXSTECRV} should resolve to a non-None price"
    )

    price = float(result.price if isinstance(result, PriceResult) else result)
    assert price > 0, f"cvxsteCRV price should be positive, got {price}"


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_convex_price_matches_underlying():
    """Convex price should match the underlying Curve LP price (within 0.1%)."""
    convex_result = await magic.get_price(
        CVX3CRV, TEST_BLOCK_3CRV, fail_to_None=True, skip_cache=True, sync=False
    )
    lp_result = await magic.get_price(
        CVX3CRV_UNDERLYING, TEST_BLOCK_3CRV, fail_to_None=True, skip_cache=True, sync=False
    )

    assert convex_result is not None, "cvx3crv price should not be None"
    assert lp_result is not None, "3crv LP price should not be None"

    convex_price = float(
        convex_result.price if isinstance(convex_result, PriceResult) else convex_result
    )
    lp_price = float(
        lp_result.price if isinstance(lp_result, PriceResult) else lp_result
    )

    assert convex_price > 0, f"Convex price should be positive, got {convex_price}"

    # Convex is 1:1 with LP — allow < 0.1% diff
    relative_diff = abs(convex_price - lp_price) / lp_price
    assert relative_diff < 0.001, (
        f"Convex price {convex_price} differs from LP price {lp_price} "
        f"by {relative_diff:.4%}, expected within 0.1%"
    )


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_convex_returns_price_result():
    """Convex pricing should return a PriceResult with descriptive source."""
    result = await magic.get_price(
        CVX3CRV, TEST_BLOCK_3CRV, fail_to_None=True, skip_cache=True, sync=False
    )
    assert result is not None
    assert isinstance(result, PriceResult), (
        f"Expected PriceResult, got {type(result)}"
    )
    assert result.path, "PriceResult should have at least one step in path"
    # Source should mention Convex
    source = result.path[0].source
    assert "Convex" in source, (
        f"Source string should mention Convex, got '{source}'"
    )
