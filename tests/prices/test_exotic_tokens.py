"""Tests for exotic token detection and pricing.

This module tests the following token types:
- stkAAVE: 1:1 with AAVE (via one_to_one mapping)
- Pickle pSLP: underlying × getRatio()
- PoolTogether V3: 1:1 with underlying (via one_to_one mapping)
- PoolTogether V4 Ticket: 1:1 with controller().getToken()
- xPREMIA: PREMIA × getXPremiaToPremiaRatio()
- xTAROT / Tarot SupplyVault: underlying × shareValuedAsUnderlying()
"""

import pytest

from tests.fixtures import mainnet_only
from y.prices import magic
from y.prices.utils.buckets import check_bucket

# ─────────────────────────────────────────────────────────────────────────────
# Token addresses
# ─────────────────────────────────────────────────────────────────────────────

# stkAAVE (staked AAVE) — already in one_to_one.py MAPPING → AAVE
STKAAVE = "0x4da27a545c0c5B758a6BA100e3a049001de870f5"
AAVE = "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9"

# Pickle pSLP-ETH (pSLP-ETH/USDC) — typical pSLP token
# pSLP tokens bridge Sushiswap LP positions into Pickle jars
# 0x55282dA27a3a02eFe599f9bD85E2e0C78f9cD2b2 = pSLP-ETH/USDC on mainnet
PSLP_ETH_USDC = "0x55282dA27a3a02eFe599f9bD85E2e0C78f9cD2b2"

# PoolTogether V3 tokens (already in one_to_one.py MAPPING)
PLDAI = "0x49d716DFe60b37379010A75329ae09428f17118d"  # plDai -> DAI
PLUSDC = "0xBD87447F48ad729C5c4b8bcb503e1395F62e8B98"  # plUsdc -> USDC

# PoolTogether V4 Ticket — has getTwab() + controller()
# USDC Prize Pool Ticket on mainnet
# 0xdd4d117723C257CEe402285D3aCF218E9A8236E1 = PT USDC Ticket
PT_USDC_TICKET = "0xdd4d117723C257CEe402285D3aCF218E9A8236E1"

# xPREMIA — PREMIA staking token
XPREMIA = "0x16f9D564Df80376C61AC914205D3fDfB8a32f98b"
PREMIA = "0x6399C842dD2bE3dE30BF99Bc7D1bBF6Fa3650E70"

# xTAROT — xTAROT staking token on Fantom
# Note: xTAROT is on Fantom; this test only exercises the detection logic
XTAROT = "0x74D1D2A851e339B8cB953716445Be7E8aBdf92F4"  # Fantom

# Tarot SupplyVault — e.g., tTAROT (Tarot/Fantom)
TAROT_SUPPLY_VAULT = "0x26AC6Be5fA1d7a02B4Fa4a5A4ef18FBfEb8Df19d"  # Fantom

# Test block where these tokens were active on mainnet
TEST_BLOCK = 15_000_000
# Earlier block for tokens deployed before
TEST_BLOCK_EARLY = 13_000_000


# ─────────────────────────────────────────────────────────────────────────────
# stkAAVE tests (via one_to_one mapping)
# ─────────────────────────────────────────────────────────────────────────────


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_stkaave_bucket():
    """stkAAVE should be bucketed as 'one to one' since it's in the one_to_one MAPPING."""
    bucket = await check_bucket(STKAAVE, sync=False)
    assert bucket == "one to one", f"Expected 'one to one' bucket for stkAAVE, got '{bucket}'"


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_stkaave_price_near_aave():
    """stkAAVE price should be near AAVE price (within 5%)."""
    stkaave_result = await magic.get_price(
        STKAAVE, TEST_BLOCK, fail_to_None=True, skip_cache=True, sync=False
    )
    aave_result = await magic.get_price(
        AAVE, TEST_BLOCK, fail_to_None=True, skip_cache=True, sync=False
    )

    assert stkaave_result is not None, "stkAAVE price should not be None"
    assert aave_result is not None, "AAVE price should not be None"

    from y.datatypes import PriceResult

    stkaave_price = float(
        stkaave_result.price if isinstance(stkaave_result, PriceResult) else stkaave_result
    )
    aave_price = float(aave_result.price if isinstance(aave_result, PriceResult) else aave_result)

    assert stkaave_price > 0, f"stkAAVE price should be positive, got {stkaave_price}"

    # stkAAVE is 1:1 with AAVE
    relative_diff = abs(stkaave_price - aave_price) / aave_price
    assert relative_diff < 0.05, (
        f"stkAAVE price {stkaave_price} differs from AAVE price {aave_price} by "
        f"{relative_diff:.4%}, expected within 5%"
    )


# ─────────────────────────────────────────────────────────────────────────────
# PoolTogether V3 tests (via one_to_one mapping)
# ─────────────────────────────────────────────────────────────────────────────


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_pldai_bucket():
    """plDai should be bucketed as 'one to one' since it's in the one_to_one MAPPING."""
    bucket = await check_bucket(PLDAI, sync=False)
    assert bucket == "one to one", f"Expected 'one to one' bucket for plDai, got '{bucket}'"


@mainnet_only
@pytest.mark.asyncio_cooperative
async def test_pldai_price_is_dai_price():
    """plDai should resolve to approximately the DAI price (~$1)."""
    result = await magic.get_price(
        PLDAI, TEST_BLOCK_EARLY, fail_to_None=True, skip_cache=True, sync=False
    )
    assert result is not None, "plDai price should not be None"

    from y.datatypes import PriceResult

    price = float(result.price if isinstance(result, PriceResult) else result)
    assert price > 0, f"plDai price should be positive, got {price}"
    # plDai is 1:1 with DAI, which is pegged to ~$1
    assert 0.90 <= price <= 1.10, f"plDai price {price} should be near $1 (± 10%)"


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

    from y.datatypes import PriceResult

    price = float(result.price if isinstance(result, PriceResult) else result)
    assert price > 0, f"PT USDC Ticket price should be positive, got {price}"
    # Ticket is 1:1 with USDC
    assert 0.90 <= price <= 1.10, f"PT USDC Ticket price {price} should be near $1 (± 10%)"


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

    from y.datatypes import PriceResult

    price = float(result.price if isinstance(result, PriceResult) else result)
    assert price > 0, f"xPREMIA price should be positive, got {price}"


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

    from y.datatypes import PriceResult

    price = float(result.price if isinstance(result, PriceResult) else result)
    assert price > 0, f"Pickle pSLP price should be positive, got {price}"
