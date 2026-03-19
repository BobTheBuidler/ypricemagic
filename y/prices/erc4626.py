"""ERC4626 vault token detection and pricing.

ERC4626 is the standard tokenized vault interface. Vaults expose:
  - ``asset()`` — the underlying token address
  - ``previewRedeem(uint256)`` — assets received for redeeming shares (includes fees)
  - ``convertToAssets(uint256)`` — assets for shares (no fees, used as fallback)

Pricing strategy:
  - Call ``previewRedeem(10**decimals)`` for per-share spot rate.
  - If ``previewRedeem`` reverts, fall back to ``convertToAssets``.
  - If both revert, return ``None`` (graceful failure, no crash).
"""

import logging
from decimal import Decimal

import a_sync
from dank_mids.exceptions import Revert
from web3.exceptions import ContractLogicError

from y import ENVIRONMENT_VARIABLES as ENVS
from y import convert
from y._decorators import stuck_coro_debugger
from y.classes.common import ERC20
from y.contracts import has_methods
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.exceptions import call_reverted
from y.utils.cache import optional_async_diskcache
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)


@a_sync.a_sync(
    default="sync",
    cache_type="memory",
    ram_cache_ttl=5 * 60,
    ram_cache_maxsize=ENVS.DEFAULT_CACHE_MAXSIZE,
)
@optional_async_diskcache
async def is_erc4626_vault(token_address: AnyAddressType) -> bool:
    """Determine whether a token is an ERC4626 vault.

    Detection checks that the contract exposes both ``asset()`` and
    ``previewRedeem(uint256)``, which together define the ERC4626 interface.
    This approach works for unverified contracts (no ABI required).

    Args:
        token_address: The address of the token to check.

    Returns:
        ``True`` if the token is an ERC4626 vault, ``False`` otherwise.

    Examples:
        >>> is_erc4626_vault("0x83F20F44975D03b1b09e64809B757c47f942BEeA")  # sDAI
        True

        >>> is_erc4626_vault("0x6B175474E89094C44Da98b954EedeAC495271d0F")  # DAI
        False
    """
    token_address = await convert.to_address_async(token_address)
    # Use no-input view methods for detection.  ``has_methods`` calls each
    # method via multicall with no arguments, so methods that require inputs
    # (like ``previewRedeem(uint256)``) may silently fail.  ``asset()`` and
    # ``totalAssets()`` are sufficient to identify the ERC4626 interface.
    return await has_methods(
        token_address,
        ("asset()(address)", "totalAssets()(uint256)"),
        all,
        sync=False,
    )


@stuck_coro_debugger
@a_sync.a_sync(default="sync")
async def get_price(
    token_address: AnyAddressType,
    block: Block | None = None,
    skip_cache: bool = ENVS.SKIP_CACHE,
) -> UsdPrice | None:
    """Get the USD price of an ERC4626 vault token.

    The price is computed as::

        underlying_price * assets_received / 10**asset_decimals

    Where ``assets_received`` comes from ``previewRedeem(10**vault_decimals)``,
    falling back to ``convertToAssets`` if ``previewRedeem`` reverts.  If both
    revert, ``None`` is returned so the caller can fall through to other price
    sources.

    Args:
        token_address: The address of the vault token.
        block: Block number at which to price. Defaults to latest.
        skip_cache: Whether to bypass the price cache.

    Returns:
        The USD price per vault token, or ``None`` if pricing is impossible.

    See Also:
        - :func:`is_erc4626_vault` for detection logic.
        - :func:`y.prices.magic.get_price` for underlying token pricing.
    """
    from y.prices import magic

    token_address = await convert.to_address_async(token_address)

    # Get the underlying asset address
    underlying_address = await raw_call(
        token_address,
        "asset()",
        output="address",
        block=block,
        return_None_on_failure=True,
        sync=False,
    )
    if not underlying_address:
        return None

    # Determine the share amount to redeem (one full share)
    vault_erc20 = ERC20(token_address, asynchronous=True)
    vault_scale = await vault_erc20.__scale__

    shares_to_redeem = int(vault_scale)
    if shares_to_redeem == 0:
        return None

    # Try previewRedeem first (captures real fees)
    via = "previewRedeem"
    assets_received = await _call_preview_redeem(token_address, shares_to_redeem, block)

    # Fall back to convertToAssets if previewRedeem reverted
    if assets_received is None:
        via = "convertToAssets"
        assets_received = await _call_convert_to_assets(token_address, shares_to_redeem, block)

    if assets_received is None or assets_received == 0:
        return None

    # Price the underlying token
    underlying_erc20 = ERC20(underlying_address, asynchronous=True)
    underlying_scale = await underlying_erc20.__scale__

    underlying_price = await magic.get_price(
        underlying_address, block=block, skip_cache=skip_cache, sync=False
    )
    if not underlying_price:
        return None

    # price per vault token = (assets_received / underlying_scale) * underlying_price
    price = (
        Decimal(assets_received)
        / Decimal(underlying_scale)
        * Decimal(str(float(underlying_price)))
    )
    return UsdPrice(price)


async def _call_preview_redeem(token_address: str, shares: int, block: Block | None) -> int | None:
    """Call ``previewRedeem(shares)`` and return the result, or ``None`` on revert."""
    try:
        result = await raw_call(
            token_address,
            "previewRedeem(uint256)",
            inputs=shares,
            output="int",
            block=block,
            return_None_on_failure=True,
            sync=False,
        )
        return result
    except (ContractLogicError, Revert) as e:
        logger.debug("previewRedeem reverted for %s at block %s: %s", token_address, block, e)
        return None
    except Exception as e:
        if call_reverted(e):
            logger.debug("previewRedeem reverted for %s at block %s: %s", token_address, block, e)
            return None
        raise


async def _call_convert_to_assets(
    token_address: str, shares: int, block: Block | None
) -> int | None:
    """Call ``convertToAssets(shares)`` and return the result, or ``None`` on revert."""
    try:
        result = await raw_call(
            token_address,
            "convertToAssets(uint256)",
            inputs=shares,
            output="int",
            block=block,
            return_None_on_failure=True,
            sync=False,
        )
        return result
    except (ContractLogicError, Revert) as e:
        logger.debug("convertToAssets reverted for %s at block %s: %s", token_address, block, e)
        return None
    except Exception as e:
        if call_reverted(e):
            logger.debug("convertToAssets reverted for %s at block %s: %s", token_address, block, e)
            return None
        raise
