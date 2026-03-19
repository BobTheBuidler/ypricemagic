"""Tests for Curve gauge token pricing.

Curve gauge tokens have symbols ending in '-gauge'. They are priced 1:1
with the underlying Curve LP token via the ``lp_token()`` view function.

Some gauge tokens are already hardcoded in ``one_to_one.py`` and will be
caught by the ``string_matchers`` bucket before reaching ``calls_only``.
This test file uses gauge addresses that are NOT in ``one_to_one.py`` so
that the dynamic ``curve_gauge.is_curve_gauge()`` detection is exercised.
"""

import pytest

from tests.fixtures import mainnet_only
from y.datatypes import PriceResult
from y.prices import magic
from y.prices.utils.buckets import check_bucket

# ─────────────────────────────────────────────────────────────────────────────
# Token addresses
# ─────────────────────────────────────────────────────────────────────────────

# steCRV-gauge: stETH/ETH Curve gauge.
# NOT in one_to_one.py — must be detected dynamically.
STETH_GAUGE = "0x182B723a58739a9c974cFDB385ceaDb237453c28"
STETH_LP = "0x06325440D014e39736583c165C2963BA99fAf14E"

# sdai-usdm-gauge: hardcoded in one_to_one.py (will bucket as "one to one").
SDAI_USDM_GAUGE = "0xcF5136C67fA8A375BaBbDf13c0307EF994b5681D"
SDAI_USDM_LP = "0x425BfB93370F14fF525aDb6EaEAcfE1f4e3b5802"

# DAI — definitely NOT a gauge token (sanity check).
DAI = "0x6B175474E89094C44Da98b954EedeAC495271d0F"

# Test blocks where gauges are deployed and active
TEST_BLOCK = 20_000_000
TEST_BLOCK_STETH = 15_000_000


# ─────────────────────────────────────────────────────────────────────────────
# Detection tests
# ─────────────────────────────────────────────────────────────────────────────


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_curve_gauge_bucket_detection():
    """A gauge NOT in one_to_one.py should be bucketed as 'curve gauge'.

    Uses steCRV-gauge (stETH/ETH) which is not in the one_to_one mapping,
    so ``check_bucket()`` must detect it dynamically via the ``curve_gauge``
    entry in calls_only.
    """
    bucket = await check_bucket(STETH_GAUGE, sync=False)
    assert bucket == "curve gauge", (
        f"Expected 'curve gauge' bucket for {STETH_GAUGE}, got '{bucket}'"
    )


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_non_gauge_not_detected():
    """A non-gauge token (DAI) should NOT be bucketed as 'curve gauge'."""
    bucket = await check_bucket(DAI, sync=False)
    assert bucket != "curve gauge", (
        f"DAI should not be bucketed as 'curve gauge', got '{bucket}'"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Pricing tests
# ─────────────────────────────────────────────────────────────────────────────


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_gauge_price_equals_lp_price():
    """Gauge price should equal the underlying LP token price (within 0.1%)."""
    gauge_result = await magic.get_price(
        STETH_GAUGE, TEST_BLOCK_STETH, fail_to_None=True, skip_cache=True, sync=False
    )
    lp_result = await magic.get_price(
        STETH_LP, TEST_BLOCK_STETH, fail_to_None=True, skip_cache=True, sync=False
    )

    assert gauge_result is not None, (
        f"Gauge {STETH_GAUGE} should resolve to a non-None price"
    )
    assert lp_result is not None, (
        f"LP {STETH_LP} should resolve to a non-None price"
    )

    gauge_price = float(
        gauge_result.price if isinstance(gauge_result, PriceResult) else gauge_result
    )
    lp_price = float(
        lp_result.price if isinstance(lp_result, PriceResult) else lp_result
    )

    assert gauge_price > 0, f"Gauge price should be positive, got {gauge_price}"

    # Gauge is 1:1 with LP — allow < 0.1% diff
    relative_diff = abs(gauge_price - lp_price) / lp_price
    assert relative_diff < 0.001, (
        f"Gauge price {gauge_price} differs from LP price {lp_price} "
        f"by {relative_diff:.4%}, expected within 0.1%"
    )


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_gauge_returns_price_result():
    """Curve gauge pricing should return a PriceResult with descriptive source."""
    result = await magic.get_price(
        STETH_GAUGE, TEST_BLOCK_STETH, fail_to_None=True, skip_cache=True, sync=False
    )
    assert result is not None
    assert isinstance(result, PriceResult), (
        f"Expected PriceResult, got {type(result)}"
    )
    assert result.path, "PriceResult should have at least one step in path"
    # Source should mention Curve gauge and LP
    source = result.path[0].source
    assert "Curve" in source or "gauge" in source.lower(), (
        f"Source string should mention Curve gauge, got '{source}'"
    )


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_hardcoded_gauge_still_resolves():
    """Gauge tokens in one_to_one.py should still resolve (via one-to-one bucket)."""
    result = await magic.get_price(
        SDAI_USDM_GAUGE, TEST_BLOCK, fail_to_None=True, skip_cache=True, sync=False
    )
    assert result is not None, (
        f"Hardcoded gauge {SDAI_USDM_GAUGE} should resolve to a non-None price"
    )

    price = float(result.price if isinstance(result, PriceResult) else result)
    assert price > 0, f"Hardcoded gauge price should be positive, got {price}"
