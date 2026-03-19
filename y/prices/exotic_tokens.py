"""Exotic token detection and pricing for various DeFi protocols.

This module handles token types that don't fit neatly into the main pricing
buckets but have well-known patterns:

- **Pickle pSLP**: Symbol starts with ``pSLP-``, has ``getRatio()`` and ``token()``.
  Price = underlying × getRatio() / 1e18.
- **PoolTogether V4 Ticket**: Has ``controller()`` + name matches
  ``'PoolTogether * Ticket'``. Price = 1:1 with ``controller().getToken()``.
- **xPREMIA**: Symbol == ``'xPREMIA'``, has ``getXPremiaToPremiaRatio()``.
  Price = PREMIA × ratio / 1e18.
- **xTAROT**: Symbol == ``'xTAROT'``, has ``shareValuedAsUnderlying()`` and ``underlying()``.
  Price = underlying × shareValuedAsUnderlying(1e18) / underlying_scale.
- **Tarot SupplyVault**: name == ``'SupplyVault'``, has ``getSupplyRate()`` + ``underlying()``.
  Same pricing as xTAROT.
"""

import logging
from decimal import Decimal

import a_sync
from brownie import ZERO_ADDRESS

from y import ENVIRONMENT_VARIABLES as ENVS
from y import convert
from y._decorators import stuck_coro_debugger
from y.classes.common import ERC20
from y.contracts import has_methods
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.utils.cache import optional_async_diskcache
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# PREMIA token address (used by xPREMIA pricing)
_PREMIA_ADDRESS = "0x6399C842dD2bE3dE30BF99Bc7D1bBF6Fa3650E70"


def _shorten_address(address: str) -> str:
    """Shorten an Ethereum address to first 6 + last 4 chars."""
    address = str(address)
    if len(address) >= 12:
        return f"{address[:6]}...{address[-4:]}"
    return address


# ═══════════════════════════════════════════════════════════════════════════
# Pickle pSLP
# ═══════════════════════════════════════════════════════════════════════════


@a_sync.a_sync(default="sync", cache_type="memory", ram_cache_ttl=5 * 60, ram_cache_maxsize=ENVS.DEFAULT_CACHE_MAXSIZE)
@stuck_coro_debugger
@optional_async_diskcache
async def is_pickle_pslp(token_address: AnyAddressType) -> bool:
    """Determine whether a token is a Pickle pSLP token.

    Detection requires:
    1. Symbol starts with ``'pSLP-'``.
    2. The contract exposes ``getRatio()`` and ``token()``.

    Args:
        token_address: The address of the token to check.

    Returns:
        ``True`` if the token is a Pickle pSLP token, ``False`` otherwise.
    """
    token_address = await convert.to_address_async(token_address)

    try:
        symbol = await ERC20(token_address, asynchronous=True).symbol
    except Exception:
        return False

    if not symbol or not symbol.startswith("pSLP-"):
        return False

    return await has_methods(
        token_address, ("getRatio()(uint256)", "token()(address)"), all, sync=False
    )


@stuck_coro_debugger
@a_sync.a_sync(default="sync")
async def get_price_pickle_pslp(
    token_address: AnyAddressType,
    block: Block | None = None,
    skip_cache: bool = ENVS.SKIP_CACHE,
) -> UsdPrice | None:
    """Get the USD price of a Pickle pSLP token.

    Price = underlying_price × getRatio() / 1e18.

    Args:
        token_address: The address of the pSLP token.
        block: Block number. Defaults to latest.
        skip_cache: Whether to bypass the price cache.

    Returns:
        The USD price per pSLP token, or ``None`` on failure.
    """
    from y.prices import magic

    token_address = await convert.to_address_async(token_address)

    underlying_address = await raw_call(
        token_address,
        "token()",
        output="address",
        block=block,
        return_None_on_failure=True,
        sync=False,
    )
    if not underlying_address or underlying_address == ZERO_ADDRESS:
        return None

    ratio_raw = await raw_call(
        token_address,
        "getRatio()",
        output="int",
        block=block,
        return_None_on_failure=True,
        sync=False,
    )
    if ratio_raw is None or ratio_raw == 0:
        return None

    ratio = Decimal(ratio_raw) / Decimal(10**18)

    underlying_price = await magic.get_price(
        underlying_address, block=block, skip_cache=skip_cache, sync=False
    )
    if not underlying_price:
        return None

    return UsdPrice(Decimal(str(float(underlying_price))) * ratio)


# ═══════════════════════════════════════════════════════════════════════════
# PoolTogether V4 Ticket
# ═══════════════════════════════════════════════════════════════════════════


@a_sync.a_sync(default="sync", cache_type="memory", ram_cache_ttl=5 * 60, ram_cache_maxsize=ENVS.DEFAULT_CACHE_MAXSIZE)
@stuck_coro_debugger
@optional_async_diskcache
async def is_pool_together_v4_ticket(token_address: AnyAddressType) -> bool:
    """Determine whether a token is a PoolTogether V4 Ticket.

    Detection requires:
    1. The contract exposes ``controller()``.
    2. The token name matches ``'PoolTogether * Ticket'``.

    Args:
        token_address: The address of the token to check.

    Returns:
        ``True`` if the token is a PoolTogether V4 Ticket, ``False`` otherwise.
    """
    token_address = await convert.to_address_async(token_address)

    if not await has_methods(
        token_address,
        ("controller()(address)",),
        all,
        sync=False,
    ):
        return False

    try:
        name = await raw_call(
            token_address,
            "name()",
            output="str",
            return_None_on_failure=True,
            sync=False,
        )
    except Exception:
        return False

    if not name:
        return False
    return name.startswith("PoolTogether ") and name.endswith(" Ticket")


@stuck_coro_debugger
@a_sync.a_sync(default="sync")
async def get_price_pool_together_v4(
    token_address: AnyAddressType,
    block: Block | None = None,
    skip_cache: bool = ENVS.SKIP_CACHE,
) -> UsdPrice | None:
    """Get the USD price of a PoolTogether V4 Ticket.

    Tickets are 1:1 with the underlying token returned by
    ``controller().getToken()``.

    Args:
        token_address: The address of the ticket token.
        block: Block number. Defaults to latest.
        skip_cache: Whether to bypass the price cache.

    Returns:
        The USD price per ticket, or ``None`` on failure.
    """
    from y.prices import magic

    token_address = await convert.to_address_async(token_address)

    controller_address = await raw_call(
        token_address,
        "controller()",
        output="address",
        block=block,
        return_None_on_failure=True,
        sync=False,
    )
    if not controller_address or controller_address == ZERO_ADDRESS:
        return None

    underlying_address = await raw_call(
        controller_address,
        "getToken()",
        output="address",
        block=block,
        return_None_on_failure=True,
        sync=False,
    )
    if not underlying_address or underlying_address == ZERO_ADDRESS:
        return None

    return await magic.get_price(
        underlying_address, block=block, skip_cache=skip_cache, sync=False
    )


# ═══════════════════════════════════════════════════════════════════════════
# xPREMIA
# ═══════════════════════════════════════════════════════════════════════════


@a_sync.a_sync(default="sync", cache_type="memory", ram_cache_ttl=5 * 60, ram_cache_maxsize=ENVS.DEFAULT_CACHE_MAXSIZE)
@stuck_coro_debugger
@optional_async_diskcache
async def is_xpremia(token_address: AnyAddressType) -> bool:
    """Determine whether a token is xPREMIA.

    Detection: symbol == ``'xPREMIA'`` and contract exposes
    ``getXPremiaToPremiaRatio()``.

    Args:
        token_address: The address of the token to check.

    Returns:
        ``True`` if the token is xPREMIA, ``False`` otherwise.
    """
    token_address = await convert.to_address_async(token_address)

    try:
        symbol = await ERC20(token_address, asynchronous=True).symbol
    except Exception:
        return False

    if symbol != "xPREMIA":
        return False

    return await has_methods(
        token_address, ("getXPremiaToPremiaRatio()(uint256)",), all, sync=False
    )


@stuck_coro_debugger
@a_sync.a_sync(default="sync")
async def get_price_xpremia(
    token_address: AnyAddressType,
    block: Block | None = None,
    skip_cache: bool = ENVS.SKIP_CACHE,
) -> UsdPrice | None:
    """Get the USD price of xPREMIA.

    Price = PREMIA_price × getXPremiaToPremiaRatio() / 1e18.

    If ``getXPremiaToPremiaRatio()`` reverts, falls back to 1:1 with PREMIA.

    Args:
        token_address: The address of the xPREMIA token.
        block: Block number. Defaults to latest.
        skip_cache: Whether to bypass the price cache.

    Returns:
        The USD price per xPREMIA, or ``None`` on failure.
    """
    from y.prices import magic

    ratio_raw = await raw_call(
        token_address,
        "getXPremiaToPremiaRatio()",
        output="int",
        block=block,
        return_None_on_failure=True,
        sync=False,
    )

    premia_price = await magic.get_price(
        _PREMIA_ADDRESS, block=block, skip_cache=skip_cache, sync=False
    )
    if not premia_price:
        return None

    if ratio_raw is None or ratio_raw == 0:
        # Fall back to 1:1 with PREMIA (older version without ratio function)
        logger.debug("xPREMIA ratio unavailable; treating as 1:1 with PREMIA")
        return UsdPrice(float(premia_price))

    ratio = Decimal(ratio_raw) / Decimal(10**18)
    return UsdPrice(Decimal(str(float(premia_price))) * ratio)


# ═══════════════════════════════════════════════════════════════════════════
# xTAROT
# ═══════════════════════════════════════════════════════════════════════════


@a_sync.a_sync(default="sync", cache_type="memory", ram_cache_ttl=5 * 60, ram_cache_maxsize=ENVS.DEFAULT_CACHE_MAXSIZE)
@stuck_coro_debugger
@optional_async_diskcache
async def is_xtarot(token_address: AnyAddressType) -> bool:
    """Determine whether a token is xTAROT.

    Detection: symbol == ``'xTAROT'`` and contract exposes
    ``shareValuedAsUnderlying(uint256)`` and ``underlying()``.

    Args:
        token_address: The address of the token to check.

    Returns:
        ``True`` if the token is xTAROT, ``False`` otherwise.
    """
    token_address = await convert.to_address_async(token_address)

    try:
        symbol = await ERC20(token_address, asynchronous=True).symbol
    except Exception:
        return False

    if symbol != "xTAROT":
        return False

    return await has_methods(
        token_address,
        ("shareValuedAsUnderlying(uint256)(uint256)", "underlying()(address)"),
        all,
        sync=False,
    )


# ═══════════════════════════════════════════════════════════════════════════
# Tarot SupplyVault
# ═══════════════════════════════════════════════════════════════════════════


@a_sync.a_sync(default="sync", cache_type="memory", ram_cache_ttl=5 * 60, ram_cache_maxsize=ENVS.DEFAULT_CACHE_MAXSIZE)
@stuck_coro_debugger
@optional_async_diskcache
async def is_tarot_supply_vault(token_address: AnyAddressType) -> bool:
    """Determine whether a token is a Tarot SupplyVault.

    Detection requires:
    1. Token name == ``'SupplyVault'``.
    2. Contract exposes ``getSupplyRate()`` and ``underlying()``.

    Args:
        token_address: The address of the token to check.

    Returns:
        ``True`` if the token is a Tarot SupplyVault, ``False`` otherwise.
    """
    token_address = await convert.to_address_async(token_address)

    if not await has_methods(
        token_address,
        ("getSupplyRate()(uint256)", "underlying()(address)"),
        all,
        sync=False,
    ):
        return False

    try:
        name = await raw_call(
            token_address,
            "name()",
            output="str",
            return_None_on_failure=True,
            sync=False,
        )
    except Exception:
        return False

    return name == "SupplyVault"


# ═══════════════════════════════════════════════════════════════════════════
# Shared pricing for xTAROT and Tarot SupplyVault
# ═══════════════════════════════════════════════════════════════════════════


@stuck_coro_debugger
@a_sync.a_sync(default="sync")
async def get_price_tarot_vault(
    token_address: AnyAddressType,
    block: Block | None = None,
    skip_cache: bool = ENVS.SKIP_CACHE,
) -> UsdPrice | None:
    """Get the USD price of an xTAROT or Tarot SupplyVault token.

    Price = underlying_price × shareValuedAsUnderlying(1e18) / underlying_scale.

    Args:
        token_address: The address of the xTAROT or SupplyVault token.
        block: Block number. Defaults to latest.
        skip_cache: Whether to bypass the price cache.

    Returns:
        The USD price per token, or ``None`` on failure.
    """
    from y.prices import magic

    token_address = await convert.to_address_async(token_address)

    underlying_address = await raw_call(
        token_address,
        "underlying()",
        output="address",
        block=block,
        return_None_on_failure=True,
        sync=False,
    )
    if not underlying_address or underlying_address == ZERO_ADDRESS:
        return None

    # shareValuedAsUnderlying(1e18) gives the underlying value per 1e18 shares
    scale = 10**18
    underlying_raw = await raw_call(
        token_address,
        "shareValuedAsUnderlying(uint256)",
        inputs=scale,
        output="int",
        block=block,
        return_None_on_failure=True,
        sync=False,
    )
    if underlying_raw is None or underlying_raw == 0:
        return None

    # Get the underlying token's scale to properly convert
    underlying_erc20 = ERC20(underlying_address, asynchronous=True)
    underlying_scale = await underlying_erc20.__scale__

    ratio = Decimal(underlying_raw) / Decimal(underlying_scale)

    underlying_price = await magic.get_price(
        underlying_address, block=block, skip_cache=skip_cache, sync=False
    )
    if not underlying_price:
        return None

    return UsdPrice(ratio * Decimal(str(float(underlying_price))))
