"""Tests for Curve gauge token pricing.

Curve gauge tokens have symbols ending in '-gauge'. They are priced 1:1
with the underlying Curve LP token via the lp_token() view function.

Hardcoded entries in one_to_one.py serve as fallback for gauges that may
not match the -gauge symbol suffix.
"""

import pytest

from tests.fixtures import mainnet_only
from y.prices import magic
from y.prices.utils.buckets import check_bucket

# Known Curve gauge tokens on mainnet (symbol ends with '-gauge')
# steCRV-gauge -> steCRV LP  (NOT hardcoded in one_to_one.py — pure dynamic detection)
# Deployed early 2021 as the stETH/ETH Curve gauge.
STETH_GAUGE = "0x182b723a58739a9c974cfdb385ceadb237453c28"
STETH_LP = "0x06325440D014e39736583c165C2963BA99fAf14E"

# sdai-usdm-gauge -> sdai-usdm LP  (hardcoded in one_to_one.py)
SDAI_USDM_GAUGE = "0xcF5136C67fA8A375BaBbDf13c0307EF994b5681D"
SDAI_USDM_LP = "0x425BfB93370F14fF525aDb6EaEAcfE1f4e3b5802"

# YFImkUSD-gauge -> YFImkUSD LP  (hardcoded in one_to_one.py)
YFI_MKUSD_GAUGE = "0x590f7e2b211Fa5Ff7840Dd3c425B543363797701"
YFI_MKUSD_LP = "0x5756bbdDC03DaB01a3900F01Fb15641C3bfcc457"

# Test block where gauges are deployed and active
TEST_BLOCK = 20_000_000
# Earlier block for the stETH gauge (deployed 2021)
TEST_BLOCK_STETH = 15_000_000


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_gauge_bucket_detection():
    """A known -gauge token (NOT in one_to_one.py) should be bucketed as 'curve gauge'.

    Uses steCRV-gauge (stETH/ETH Curve gauge) which is not hardcoded in
    one_to_one.py, so check_bucket() must detect it dynamically via the
    curve_gauge.is_curve_gauge() function in the calls_only dict.
    """
    bucket = await check_bucket(STETH_GAUGE, sync=False)
    assert (
        bucket == "curve gauge"
    ), f"Expected 'curve gauge' bucket for {STETH_GAUGE}, got '{bucket}'"


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_gauge_by_symbol():
    """A known -gauge token should resolve to its underlying LP price (within 0.1%)."""
    gauge_price_result = await magic.get_price(
        SDAI_USDM_GAUGE, TEST_BLOCK, fail_to_None=True, skip_cache=True, sync=False
    )
    lp_price_result = await magic.get_price(
        SDAI_USDM_LP, TEST_BLOCK, fail_to_None=True, skip_cache=True, sync=False
    )

    assert (
        gauge_price_result is not None
    ), f"Gauge {SDAI_USDM_GAUGE} should resolve to a non-None price"
    assert (
        lp_price_result is not None
    ), f"LP token {SDAI_USDM_LP} should resolve to a non-None price"

    from y.datatypes import PriceResult

    gauge_price = (
        float(gauge_price_result.price)
        if isinstance(gauge_price_result, PriceResult)
        else float(gauge_price_result)
    )
    lp_price = (
        float(lp_price_result.price)
        if isinstance(lp_price_result, PriceResult)
        else float(lp_price_result)
    )

    assert gauge_price > 0, f"Gauge price should be positive, got {gauge_price}"

    # Gauge should be priced 1:1 with LP (within 0.1%)
    relative_diff = abs(gauge_price - lp_price) / lp_price
    assert relative_diff < 0.001, (
        f"Gauge price {gauge_price} differs from LP price {lp_price} by {relative_diff:.4%}, "
        "expected within 0.1%"
    )


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_hardcoded_gauge_still_works():
    """Hardcoded gauge entries in one_to_one.py should still resolve correctly.

    Even if a gauge token matches the 'curve gauge' bucket via symbol detection,
    gauges explicitly in one_to_one.py should still resolve (they may be caught
    by the 'one to one' bucket first since string_matchers is checked before calls_only).
    """
    result = await magic.get_price(
        YFI_MKUSD_GAUGE, TEST_BLOCK, fail_to_None=True, skip_cache=True, sync=False
    )
    assert (
        result is not None
    ), f"Hardcoded gauge {YFI_MKUSD_GAUGE} should resolve to a non-None price"

    from y.datatypes import PriceResult

    price = float(result.price) if isinstance(result, PriceResult) else float(result)
    assert price > 0, f"Hardcoded gauge price should be positive, got {price}"
