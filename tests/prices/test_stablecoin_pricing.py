"""Tests for stablecoin pricing with real market prices.

Only USDC is hardcoded to $1 via the 'stable usd' bucket. All other stablecoins
(USDT, DAI, etc.) get real prices from Chainlink oracles or DEX pools.

These tests verify the fix that prevents silently assuming non-USDC stablecoins
are worth exactly $1, which was incorrect during depeg events.
"""

import pytest

from tests.fixtures import mainnet_only
from y.prices import magic
from y.prices.utils.buckets import check_bucket

# Mainnet addresses
USDC_ADDRESS = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
USDT_ADDRESS = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
DAI_ADDRESS = "0x6B175474E89094C44Da98b954EedeAC495271d0F"

# MIC (Mithril Cash) - paired only with USDT on Uniswap V2 at early blocks.
# At block 12500000, the only liquid pool for MIC was MIC/USDT, making it
# an ideal test case for the USDT→USDC path extension.
MIC_ADDRESS = "0x368B3a58B5f49392e5C9E4C998cb0bB966752E51"
MIC_TEST_BLOCK = 12_500_000


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_usdt_real_price():
    """USDT should return a real market price, not hardcoded $1.

    The source should not be 'stable usd' — it should come from Chainlink or a DEX pool.
    The price should be near $1 under normal market conditions.
    """
    # Use a recent block where USDT is not depegged
    from y.datatypes import PriceResult

    result = await magic.get_price(USDT_ADDRESS, skip_cache=True, sync=False)
    price = result.price if isinstance(result, PriceResult) else float(result)

    assert price is not None, "USDT price should not be None"
    assert (
        0.95 <= price <= 1.05
    ), f"USDT price {price} not in expected range [0.95, 1.05] under normal conditions"

    # Verify USDT does NOT get the 'stable usd' bucket
    bucket = await check_bucket(USDT_ADDRESS, sync=False)
    assert bucket != "stable usd", (
        f"USDT should not have 'stable usd' bucket (got '{bucket}'); "
        "only USDC should be hardcoded to $1"
    )


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_dai_real_price():
    """DAI should return a real market price, not hardcoded $1.

    The source should not be 'stable usd' — it should come from Chainlink or a DEX pool.
    The price should be near $1 under normal market conditions.
    """
    from y.datatypes import PriceResult

    result = await magic.get_price(DAI_ADDRESS, skip_cache=True, sync=False)
    price = result.price if isinstance(result, PriceResult) else float(result)

    assert price is not None, "DAI price should not be None"
    assert (
        0.95 <= price <= 1.05
    ), f"DAI price {price} not in expected range [0.95, 1.05] under normal conditions"

    # Verify DAI does NOT get the 'stable usd' bucket
    bucket = await check_bucket(DAI_ADDRESS, sync=False)
    assert bucket != "stable usd", (
        f"DAI should not have 'stable usd' bucket (got '{bucket}'); "
        "only USDC should be hardcoded to $1"
    )


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_mic_resolves_via_usdt():
    """MIC at block 12500000 should resolve through USDT with USDC as terminal token.

    At block 12500000, MIC was only liquid against USDT on Uniswap V2.
    The price resolution should:
    1. Find the MIC/USDT pool via get_path_to_stables
    2. Extend the path with USDC (MIC → USDT → USDC) OR
       multiply the MIC/USDT price by the real USDT/USD price
    3. Return a non-zero USD price
    """
    from y.datatypes import PriceResult

    result = await magic.get_price(
        MIC_ADDRESS, MIC_TEST_BLOCK, fail_to_None=True, skip_cache=True, sync=False
    )
    assert (
        result is not None
    ), f"MIC at block {MIC_TEST_BLOCK} should resolve to a non-None price via USDT path"

    price = result.price if isinstance(result, PriceResult) else float(result)
    assert price > 0, f"MIC price should be positive, got {price}"

    # Check that the trade path goes through USDT (if PriceResult is available)
    if isinstance(result, PriceResult) and result.steps:
        path_addresses = [step.address for step in result.steps if hasattr(step, "address")]
        assert any(addr == USDT_ADDRESS for addr in path_addresses) or any(
            USDT_ADDRESS in str(step) for step in result.steps
        ), f"MIC price resolution should pass through USDT at block {MIC_TEST_BLOCK}"
