"""Curve gauge token detection and pricing.

Curve gauge tokens have symbols ending in '-gauge'. They are priced 1:1
with the underlying Curve LP token, which is returned by the ``lp_token()``
view function present on all Curve gauge versions (V1–V4, RewardsOnly, NG).
"""

import logging

import a_sync
from brownie import ZERO_ADDRESS

from y import ENVIRONMENT_VARIABLES as ENVS
from y import convert
from y._decorators import stuck_coro_debugger
from y.classes.common import ERC20
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.exceptions import call_reverted
from y.utils.cache import optional_async_diskcache
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)


@a_sync.a_sync(default="sync", cache_type="memory", ram_cache_ttl=5 * 60, ram_cache_maxsize=ENVS.DEFAULT_CACHE_MAXSIZE)
@optional_async_diskcache
async def is_curve_gauge(token_address: AnyAddressType) -> bool:
    """Determine whether a token is a Curve gauge.

    Detection uses two criteria:
    1. The token's symbol ends with ``-gauge`` (case-insensitive).
    2. A call to ``lp_token()`` on the contract succeeds and returns a
       non-zero address.

    Both conditions must be satisfied.  The symbol check is a cheap
    fast-path; the ``lp_token()`` call confirms the contract actually
    implements the Curve gauge interface (all V1–V4, RewardsOnly, and NG
    gauges expose this method).

    Args:
        token_address: The address of the token to check.

    Returns:
        ``True`` if the token is a Curve gauge, ``False`` otherwise.

    Examples:
        >>> is_curve_gauge("0xcF5136C67fA8A375BaBbDf13c0307EF994b5681D")
        True

        >>> is_curve_gauge("0x6B175474E89094C44Da98b954EedeAC495271d0F")
        False
    """
    token_address = await convert.to_address_async(token_address)

    # Fast path: check symbol suffix (no RPC call needed for cached symbols)
    try:
        symbol = await ERC20(token_address, asynchronous=True).symbol
    except Exception:
        return False

    if not symbol or not symbol.lower().endswith("-gauge"):
        return False

    # Confirm the contract exposes lp_token() — present on all Curve gauge
    # versions
    lp = await _get_lp_token(token_address)
    return lp is not None


@stuck_coro_debugger
async def _get_lp_token(token_address: str) -> str | None:
    """Return the underlying Curve LP token address for a gauge, or ``None``.

    Calls ``lp_token()`` on the gauge contract.  Returns ``None`` if the call
    reverts or returns the zero address.

    Args:
        token_address: The gauge contract address (already checksummed).

    Returns:
        The LP token checksum address, or ``None`` if not available.
    """
    try:
        lp = await raw_call(
            token_address,
            "lp_token()",
            output="address",
            return_None_on_failure=True,
            sync=False,
        )
    except Exception as e:
        if call_reverted(e):
            return None
        raise
    if not lp or lp == ZERO_ADDRESS:
        return None
    return await convert.to_address_async(lp)


@stuck_coro_debugger
@a_sync.a_sync(default="sync")
async def get_price(
    token_address: AnyAddressType,
    block: Block | None = None,
    skip_cache: bool = ENVS.SKIP_CACHE,
) -> UsdPrice | None:
    """Get the USD price of a Curve gauge token.

    Curve gauges are 1:1 with their underlying LP token, so the price is
    fetched directly from the LP token via the normal pricing pipeline.

    Args:
        token_address: The address of the gauge token.
        block: The block number at which to get the price.  Defaults to latest.
        skip_cache: Whether to bypass the price cache.

    Returns:
        The USD price of the gauge (equals the LP token price), or ``None``
        if the underlying LP token cannot be resolved or priced.

    See Also:
        - :func:`is_curve_gauge` for detection logic.
        - :func:`y.prices.magic.get_price` for the underlying price fetching.
    """
    from y.prices import magic

    token_address = await convert.to_address_async(token_address)
    lp_token = await _get_lp_token(token_address)
    if lp_token is None:
        logger.warning("Could not resolve LP token for gauge %s", token_address)
        return None
    return await magic.get_price(
        lp_token, block=block, skip_cache=skip_cache, sync=False
    )
