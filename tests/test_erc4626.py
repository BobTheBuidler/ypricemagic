"""Tests for ERC4626 vault detection and pricing.

This module tests:
- Detection via is_erc4626_vault (has_methods check)
- Pricing via previewRedeem with sDAI as the primary test token
- Bucket registration and dispatch
- PriceResult with descriptive source string
"""

import pytest

from tests.fixtures import mainnet_only
from y.datatypes import PriceResult
from y.prices import erc4626, magic
from y.prices.utils.buckets import check_bucket

# ─────────────────────────────────────────────────────────────────────────────
# Token addresses
# ─────────────────────────────────────────────────────────────────────────────

# sDAI (Savings DAI) — canonical ERC4626 vault on mainnet
SDAI = "0x83F20F44975D03b1b09e64809B757c47f942BEeA"

# DAI — the underlying asset of sDAI (NOT an ERC4626 vault)
DAI = "0x6B175474E89094C44Da98b954EedeAC495271d0F"

# USDC — definitely not an ERC4626 vault
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

# sDAI was deployed around block 17_139_875 (May 2023).
# Use a block well after deployment for deterministic testing.
TEST_BLOCK = 18_000_000


# ─────────────────────────────────────────────────────────────────────────────
# Detection tests
# ─────────────────────────────────────────────────────────────────────────────


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_is_erc4626_vault_sdai():
    """sDAI should be detected as an ERC4626 vault."""
    result = await erc4626.is_erc4626_vault(SDAI, sync=False)
    assert result is True, f"sDAI should be detected as ERC4626 vault, got {result}"


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_is_not_erc4626_vault_dai():
    """DAI should NOT be detected as an ERC4626 vault."""
    result = await erc4626.is_erc4626_vault(DAI, sync=False)
    assert result is False, f"DAI should not be detected as ERC4626 vault, got {result}"


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_is_not_erc4626_vault_usdc():
    """USDC should NOT be detected as an ERC4626 vault."""
    result = await erc4626.is_erc4626_vault(USDC, sync=False)
    assert result is False, f"USDC should not be detected as ERC4626 vault, got {result}"


# ─────────────────────────────────────────────────────────────────────────────
# Bucket tests
# ─────────────────────────────────────────────────────────────────────────────


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_erc4626_bucket():
    """sDAI should be bucketed as 'erc4626 vault'."""
    bucket = await check_bucket(SDAI, sync=False)
    assert bucket == "erc4626 vault", (
        f"Expected 'erc4626 vault' bucket for sDAI, got '{bucket}'"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Pricing tests
# ─────────────────────────────────────────────────────────────────────────────


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_sdai_price_positive():
    """sDAI should resolve to a positive price."""
    result = await magic.get_price(
        SDAI, TEST_BLOCK, fail_to_None=True, skip_cache=True, sync=False
    )
    assert result is not None, "sDAI price should not be None"

    price = float(result.price if isinstance(result, PriceResult) else result)
    assert price > 0, f"sDAI price should be positive, got {price}"


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_sdai_price_greater_than_dai():
    """sDAI should be worth more than DAI since it accrues DSR interest."""
    sdai_result = await magic.get_price(
        SDAI, TEST_BLOCK, fail_to_None=True, skip_cache=True, sync=False
    )
    dai_result = await magic.get_price(
        DAI, TEST_BLOCK, fail_to_None=True, skip_cache=True, sync=False
    )
    assert sdai_result is not None, "sDAI price should not be None"
    assert dai_result is not None, "DAI price should not be None"

    sdai_price = float(sdai_result.price if isinstance(sdai_result, PriceResult) else sdai_result)
    dai_price = float(dai_result.price if isinstance(dai_result, PriceResult) else dai_result)

    assert sdai_price > dai_price, (
        f"sDAI ({sdai_price}) should be worth more than DAI ({dai_price}) "
        "due to DSR interest accrual"
    )


# ─────────────────────────────────────────────────────────────────────────────
# PriceResult tests
# ─────────────────────────────────────────────────────────────────────────────


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_sdai_returns_price_result():
    """sDAI pricing should return a PriceResult with descriptive source."""
    result = await magic.get_price(
        SDAI, TEST_BLOCK, fail_to_None=True, skip_cache=True, sync=False
    )
    assert result is not None
    assert isinstance(result, PriceResult), f"Expected PriceResult, got {type(result)}"
    assert result.path, "PriceResult should have at least one step in path"
    source = result.path[0].source
    assert "ERC4626" in source, f"Source should mention 'ERC4626', got '{source}'"
    assert "sDAI" in source, f"Source should mention 'sDAI', got '{source}'"
    assert "DAI" in source, f"Source should mention underlying 'DAI', got '{source}'"
    assert "previewRedeem" in source, f"Source should mention 'previewRedeem', got '{source}'"


# ─────────────────────────────────────────────────────────────────────────────
# Direct pricing function tests
# ─────────────────────────────────────────────────────────────────────────────


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_erc4626_get_price_direct():
    """Direct call to erc4626.get_price should return a valid price."""
    price = await erc4626.get_price(
        SDAI, block=TEST_BLOCK, skip_cache=True, sync=False
    )
    assert price is not None, "erc4626.get_price should return a non-None price for sDAI"
    assert float(price) > 0, f"erc4626.get_price should return positive price, got {price}"


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_erc4626_get_price_non_vault_returns_none():
    """erc4626.get_price on a non-vault token should return None."""
    price = await erc4626.get_price(
        DAI, block=TEST_BLOCK, skip_cache=True, sync=False
    )
    # DAI doesn't have asset() so it should return None
    assert price is None, f"DAI is not an ERC4626 vault, expected None, got {price}"
