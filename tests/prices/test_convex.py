"""Tests for Convex LP token detection and pricing.

This module tests both the static-mapping path and the new dynamic detection
path in ``y.prices.convex``:

- Static mapping: 5 hardcoded ``cvxToken → curveLPToken`` entries (zero RPC calls).
- Dynamic detection: ``operator()`` call → booster verification → ``poolInfo()``
  iteration to discover the underlying Curve LP token.
"""

import pytest

from tests.fixtures import mainnet_only
from y.prices import magic
from y.prices.convex import get_underlying_lp, is_convex_lp
from y.prices.utils.buckets import check_bucket

# ─────────────────────────────────────────────────────────────────────────────
# Token addresses
# ─────────────────────────────────────────────────────────────────────────────

# cvx3CRV — in the static MAPPING (fast-path)
CVX3CRV = "0x30D9410ED1D5DA1F6C8391af5338C93ab8d4035C"
THREE_CRV = "0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490"

# cvxsteCRV — NOT in the static MAPPING; must be detected dynamically via operator()
# Convex deposit token for the Curve stETH/ETH pool
# operator() → Convex Booster (0xF403C135812408BFbE8713b5A23a04b3D48AAE31)
# pool_lptoken = steCRV (0x06325440D014e39736583c165C2963BA99fAf14E)
CVXSTECRV = "0x9518c9063eB0262D791f38d8d6Eb0aca33c63ed0"
STECRV_LP = "0x06325440D014e39736583c165C2963BA99fAf14E"

# A normal ERC20 (DAI) — should NOT be detected as Convex LP
DAI = "0x6B175474E89094C44Da98b954EedeAC495271d0F"

# Test block where Convex and these tokens are all live on mainnet
TEST_BLOCK = 15_000_000


# ─────────────────────────────────────────────────────────────────────────────
# Static mapping tests
# ─────────────────────────────────────────────────────────────────────────────


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_static_cvx3crv_is_convex_lp():
    """A token in the static MAPPING should be detected as a Convex LP."""
    result = await is_convex_lp(CVX3CRV, sync=False)
    assert result is True, f"Expected cvx3CRV {CVX3CRV} to be detected as Convex LP"


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_static_cvx3crv_underlying():
    """get_underlying_lp for a static-mapped token should return the known LP address."""
    lp = await get_underlying_lp(CVX3CRV, sync=False)
    assert lp is not None, "Expected a non-None LP for cvx3CRV"
    assert (
        lp.lower() == THREE_CRV.lower()
    ), f"Expected underlying LP {THREE_CRV} for cvx3CRV, got {lp}"


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_static_cvx3crv_bucket():
    """cvx3CRV should be bucketed as 'convex' via the calls_only detection."""
    bucket = await check_bucket(CVX3CRV, sync=False)
    assert bucket == "convex", f"Expected 'convex' bucket for cvx3CRV, got '{bucket}'"


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_static_cvx3crv_price():
    """cvx3CRV should resolve to a nonzero USD price."""
    result = await magic.get_price(
        CVX3CRV, TEST_BLOCK, fail_to_None=True, skip_cache=True, sync=False
    )
    assert result is not None, "cvx3CRV price should not be None"

    from y.datatypes import PriceResult

    price = float(result.price if isinstance(result, PriceResult) else result)
    assert price > 0, f"cvx3CRV price should be positive, got {price}"


# ─────────────────────────────────────────────────────────────────────────────
# Dynamic detection tests
# ─────────────────────────────────────────────────────────────────────────────


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_dynamic_cvxstecrv_is_convex_lp():
    """cvxsteCRV (NOT in static MAPPING) should be dynamically detected as Convex LP."""
    result = await is_convex_lp(CVXSTECRV, sync=False)
    assert result is True, f"Expected cvxsteCRV {CVXSTECRV} to be dynamically detected as Convex LP"


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_dynamic_cvxstecrv_underlying():
    """get_underlying_lp for cvxsteCRV should return the steCRV LP address."""
    lp = await get_underlying_lp(CVXSTECRV, sync=False)
    assert lp is not None, "Expected a non-None LP for cvxsteCRV"
    assert (
        lp.lower() == STECRV_LP.lower()
    ), f"Expected underlying LP {STECRV_LP} for cvxsteCRV, got {lp}"


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_dynamic_cvxstecrv_bucket():
    """cvxsteCRV should be bucketed as 'convex' via the dynamic operator() detection."""
    bucket = await check_bucket(CVXSTECRV, sync=False)
    assert bucket == "convex", f"Expected 'convex' bucket for cvxsteCRV, got '{bucket}'"


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_dynamic_cvxstecrv_price():
    """cvxsteCRV should resolve to a nonzero USD price (priced 1:1 with steCRV LP)."""
    result = await magic.get_price(
        CVXSTECRV, TEST_BLOCK, fail_to_None=True, skip_cache=True, sync=False
    )
    assert result is not None, "cvxsteCRV price should not be None"

    from y.datatypes import PriceResult

    price = float(result.price if isinstance(result, PriceResult) else result)
    assert price > 0, f"cvxsteCRV price should be positive, got {price}"


# ─────────────────────────────────────────────────────────────────────────────
# Negative detection tests
# ─────────────────────────────────────────────────────────────────────────────


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_dai_is_not_convex_lp():
    """A regular ERC20 (DAI) should NOT be detected as a Convex LP."""
    result = await is_convex_lp(DAI, sync=False)
    assert result is False, f"Expected DAI {DAI} to NOT be detected as Convex LP"


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_dai_underlying_is_none():
    """get_underlying_lp for a non-Convex token should return None."""
    lp = await get_underlying_lp(DAI, sync=False)
    assert lp is None, f"Expected None LP for DAI, got {lp}"
