"""Tests for exotic token detection and pricing.

This module tests the following exotic token types:
- Pickle pSLP: underlying × getRatio()
- PoolTogether V4 Ticket: 1:1 with controller().getToken()
- xPREMIA: PREMIA × getXPremiaToPremiaRatio()
- xTAROT: Fantom-only (skipped on mainnet)
- Tarot SupplyVault: Fantom-only (skipped on mainnet)
"""

import pytest

from tests.fixtures import mainnet_only
from y.datatypes import PriceResult
from y.prices import magic
from y.prices.utils.buckets import check_bucket

# ─────────────────────────────────────────────────────────────────────────────
# Token addresses
# ─────────────────────────────────────────────────────────────────────────────

# Pickle pSushi USDC/ETH (pSLP) on mainnet
PSLP_ETH_USDC = "0x8c2D16B7F6D3F989eb4878EcF13D695A7d504E43"

# PoolTogether V4 USDC Ticket on mainnet
PT_USDC_TICKET = "0xdd4d117723C257CEe402285D3aCF218E9A8236E1"

# xPREMIA (PremiaStaking) on mainnet
XPREMIA = "0x16f9D564Df80376C61AC914205D3fDff7057d610"
PREMIA = "0x6399C842dD2bE3dE30BF99Bc7D1bBF6Fa3650E70"

# xTAROT on Fantom
XTAROT = "0x74D1D2A851e339B8cB953716445Be7E8aBdf92F4"

# Tarot SupplyVault on Fantom
TAROT_SUPPLY_VAULT = "0x26AC6Be5fA1d7a02B4Fa4a5A4ef18FBfEb8Df19d"

# Test blocks where tokens were active on mainnet
TEST_BLOCK = 15_000_000
TEST_BLOCK_EARLY = 13_000_000


# ─────────────────────────────────────────────────────────────────────────────
# Pickle pSLP tests
# ─────────────────────────────────────────────────────────────────────────────


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_pickle_pslp_bucket():
    """A Pickle pSLP token should be bucketed as 'pickle pslp'."""
    bucket = await check_bucket(PSLP_ETH_USDC, sync=False)
    assert (
        bucket == "pickle pslp"
    ), f"Expected 'pickle pslp' bucket for {PSLP_ETH_USDC}, got '{bucket}'"


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_pickle_pslp_price():
    """A Pickle pSLP token should resolve to a nonzero price."""
    result = await magic.get_price(
        PSLP_ETH_USDC, TEST_BLOCK_EARLY, fail_to_None=True, skip_cache=True, sync=False
    )
    assert result is not None, f"pSLP-ETH/USDC {PSLP_ETH_USDC} price should not be None"

    price = float(result.price if isinstance(result, PriceResult) else result)
    assert price > 0, f"Pickle pSLP price should be positive, got {price}"


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_pickle_pslp_returns_price_result():
    """Pickle pSLP pricing should return a PriceResult with descriptive source."""
    result = await magic.get_price(
        PSLP_ETH_USDC, TEST_BLOCK_EARLY, fail_to_None=True, skip_cache=True, sync=False
    )
    assert result is not None
    assert isinstance(result, PriceResult), f"Expected PriceResult, got {type(result)}"
    assert result.path, "PriceResult should have at least one step in path"
    source = result.path[0].source
    assert "Pickle" in source or "pSLP" in source, (
        f"Source string should mention Pickle/pSLP, got '{source}'"
    )


# ─────────────────────────────────────────────────────────────────────────────
# PoolTogether V4 Ticket tests
# ─────────────────────────────────────────────────────────────────────────────


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_pool_together_v4_bucket():
    """A PoolTogether V4 Ticket should be bucketed as 'pool together v4 ticket'."""
    bucket = await check_bucket(PT_USDC_TICKET, sync=False)
    assert (
        bucket == "pool together v4 ticket"
    ), f"Expected 'pool together v4 ticket' for {PT_USDC_TICKET}, got '{bucket}'"


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_pool_together_v4_price():
    """PoolTogether V4 USDC Ticket should resolve to approximately $1 (pegged to USDC)."""
    result = await magic.get_price(
        PT_USDC_TICKET, TEST_BLOCK, fail_to_None=True, skip_cache=True, sync=False
    )
    assert result is not None, "PT USDC Ticket price should not be None"

    price = float(result.price if isinstance(result, PriceResult) else result)
    assert price > 0, f"PT USDC Ticket price should be positive, got {price}"
    # Ticket is 1:1 with USDC
    assert 0.90 <= price <= 1.10, f"PT USDC Ticket price {price} should be near $1 (± 10%)"


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_pool_together_v4_returns_price_result():
    """PoolTogether V4 pricing should return a PriceResult with descriptive source."""
    result = await magic.get_price(
        PT_USDC_TICKET, TEST_BLOCK, fail_to_None=True, skip_cache=True, sync=False
    )
    assert result is not None
    assert isinstance(result, PriceResult), f"Expected PriceResult, got {type(result)}"


# ─────────────────────────────────────────────────────────────────────────────
# xPREMIA tests
# ─────────────────────────────────────────────────────────────────────────────


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_xpremia_bucket():
    """xPREMIA should be bucketed as 'xpremia'."""
    bucket = await check_bucket(XPREMIA, sync=False)
    assert bucket == "xpremia", f"Expected 'xpremia' bucket for xPREMIA, got '{bucket}'"


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_xpremia_price():
    """xPREMIA should resolve to a nonzero price related to PREMIA."""
    result = await magic.get_price(
        XPREMIA, TEST_BLOCK, fail_to_None=True, skip_cache=True, sync=False
    )
    assert result is not None, "xPREMIA price should not be None"

    price = float(result.price if isinstance(result, PriceResult) else result)
    assert price > 0, f"xPREMIA price should be positive, got {price}"


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_xpremia_returns_price_result():
    """xPREMIA pricing should return a PriceResult with descriptive source."""
    result = await magic.get_price(
        XPREMIA, TEST_BLOCK, fail_to_None=True, skip_cache=True, sync=False
    )
    assert result is not None
    assert isinstance(result, PriceResult), f"Expected PriceResult, got {type(result)}"


# ─────────────────────────────────────────────────────────────────────────────
# xTAROT tests (Fantom only — skipped on mainnet)
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.skip(reason="Fantom-only")
@pytest.mark.asyncio_cooperative
async def test_xtarot_bucket():
    """xTAROT should be bucketed as 'xtarot'."""
    bucket = await check_bucket(XTAROT, sync=False)
    assert bucket == "xtarot", f"Expected 'xtarot' bucket for xTAROT, got '{bucket}'"


@pytest.mark.skip(reason="Fantom-only")
@pytest.mark.asyncio_cooperative
async def test_xtarot_price():
    """xTAROT should resolve to a nonzero price related to the underlying TAROT token."""
    result = await magic.get_price(
        XTAROT, 25_000_000, fail_to_None=True, skip_cache=True, sync=False
    )
    assert result is not None, "xTAROT price should not be None"

    price = float(result.price if isinstance(result, PriceResult) else result)
    assert price > 0, f"xTAROT price should be positive, got {price}"


# ─────────────────────────────────────────────────────────────────────────────
# Tarot SupplyVault tests (Fantom only — skipped on mainnet)
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.skip(reason="Fantom-only")
@pytest.mark.asyncio_cooperative
async def test_tarot_supply_vault_bucket():
    """A Tarot SupplyVault should be bucketed as 'tarot supply vault'."""
    bucket = await check_bucket(TAROT_SUPPLY_VAULT, sync=False)
    assert (
        bucket == "tarot supply vault"
    ), f"Expected 'tarot supply vault' bucket for {TAROT_SUPPLY_VAULT}, got '{bucket}'"


@pytest.mark.skip(reason="Fantom-only")
@pytest.mark.asyncio_cooperative
async def test_tarot_supply_vault_price():
    """A Tarot SupplyVault should resolve to a nonzero price."""
    result = await magic.get_price(
        TAROT_SUPPLY_VAULT, 25_000_000, fail_to_None=True, skip_cache=True, sync=False
    )
    assert result is not None, "Tarot SupplyVault price should not be None"

    price = float(result.price if isinstance(result, PriceResult) else result)
    assert price > 0, f"Tarot SupplyVault price should be positive, got {price}"
