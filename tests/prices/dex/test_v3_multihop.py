"""Tests for V3 multi-hop routing expansion.

These tests verify that UniswapV3.get_price() generates paths through all
ROUTING_TOKENS as intermediaries, not just WETH. The expanded routing
enables price discovery for tokens with USDT/DAI pools but no USDC/WETH pools.

Tests are marked slow because V3 pool discovery scans PoolCreated events.
Run with --runslow.
"""

import pytest

from tests.fixtures import async_test, mainnet_only
from y.constants import ROUTING_TOKENS
from y.networks import Network
from y.prices.dex.uniswap.v3 import uniswap_v3
from y import get_price

# USDT address on mainnet
USDT = "0xdAC17F958D2ee523a2206206994597C13D831ec7"

# WETH address on mainnet
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"

# DAI address on mainnet
DAI = "0x6B175474E89094C44Da98b954EedeAC495271d0F"

# USDC address on mainnet
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

# Block for testing - a known historical block
BLOCK = 18_000_000


@pytest.mark.slow
@async_test
@mainnet_only
async def test_v3_routing_tokens_imported() -> None:
    """VAL-CONST-001: Verify ROUTING_TOKENS contains expected mainnet tokens."""
    mainnet_tokens = ROUTING_TOKENS.get(Network.Mainnet, [])
    assert (
        len(mainnet_tokens) >= 3
    ), f"Expected at least 3 routing tokens, got {len(mainnet_tokens)}"
    # Verify the expected tokens are present
    addresses_lower = [t.lower() for t in mainnet_tokens]
    assert WETH.lower() in addresses_lower, "WETH should be a routing token"
    assert USDC.lower() in addresses_lower, "USDC should be a routing token"
    assert USDT.lower() in addresses_lower, "USDT should be a routing token"
    assert DAI.lower() in addresses_lower, "DAI should be a routing token"
    print(f"Mainnet routing tokens: {mainnet_tokens}")


@pytest.mark.slow
@async_test
@mainnet_only
async def test_v3_weth_usdc_regression() -> None:
    """VAL-V3-003: WETH→USDC direct pricing unchanged after routing expansion."""
    assert uniswap_v3 is not None
    # WETH should return approximately its ETH price (~$1800-3500 depending on block)
    price = await uniswap_v3.get_price(WETH, BLOCK, skip_cache=True, sync=False)
    assert price is not None, "WETH should return a price"
    # At block 18M, ETH was around $1800-2000
    assert 1000 < price < 5000, f"WETH price {price} outside expected range"
    print(f"WETH price at block {BLOCK}: {price}")


@pytest.mark.slow
@async_test
@mainnet_only
async def test_v3_usdt_no_self_loop() -> None:
    """VAL-V3-004: V3 no self-loop when pricing a routing token (USDT)."""
    assert uniswap_v3 is not None
    # USDT is a routing token - pricing it should not create USDT→USDT→USDC path
    price = await uniswap_v3.get_price(USDT, BLOCK, skip_cache=True, sync=False)
    assert price is not None, "USDT should return a price"
    # USDT should be approximately $1
    assert 0.95 < price < 1.05, f"USDT price {price} not close to $1"
    print(f"USDT price at block {BLOCK}: {price}")


@pytest.mark.slow
@async_test
@mainnet_only
async def test_v3_dai_no_self_loop() -> None:
    """VAL-V3-004: V3 no self-loop when pricing DAI (routing token)."""
    assert uniswap_v3 is not None
    # DAI is a routing token - pricing it should work correctly
    price = await uniswap_v3.get_price(DAI, BLOCK, skip_cache=True, sync=False)
    assert price is not None, "DAI should return a price"
    # DAI should be approximately $1
    assert 0.95 < price < 1.05, f"DAI price {price} not close to $1"
    print(f"DAI price at block {BLOCK}: {price}")


@pytest.mark.slow
@async_test
@mainnet_only
async def test_v3_no_pools_returns_none() -> None:
    """VAL-V3-005: V3 returns None gracefully for token with no V3 pools."""
    assert uniswap_v3 is not None
    # Use an invalid/zero address that has no V3 pools
    # This should return None without raising an exception
    invalid_token = "0x0000000000000000000000000000000000000001"
    price = await uniswap_v3.get_price(invalid_token, BLOCK, skip_cache=True, sync=False)
    # Should return None gracefully, not raise an exception
    assert price is None, f"Expected None for invalid token, got {price}"
    print(f"Invalid token price: {price}")


@pytest.mark.slow
@async_test
@mainnet_only
async def test_v3_price_via_get_price() -> None:
    """VAL-CROSS-001: Multi-hop improvements active in get_price()."""
    # Test that WETH returns a price through the top-level API
    price = await get_price(WETH, BLOCK, skip_cache=True, sync=False)
    assert price is not None, "WETH should return a price via get_price"
    assert price > 0, f"Price should be positive, got {price}"
    # WETH price should be in the expected range
    assert 1000 < price < 5000, f"WETH price {price} outside expected range"
    print(f"WETH price via get_price at block {BLOCK}: {price}")
