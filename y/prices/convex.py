"""Convex LP token detection and pricing.

Convex LP tokens (prefixed with ``cvx``) wrap Curve LP tokens deposited in the
Convex Finance booster.  Detection works in two stages:

1. **Static mapping** – a hardcoded ``MAPPING`` of known ``cvxToken → curveLPToken``
   addresses provides instant, zero-RPC lookup for the most common tokens.

2. **Dynamic detection** – for tokens not in the static mapping, the module
   calls ``operator()`` on the token to obtain the Convex booster address, then
   verifies the booster implements ``poolLength()`` and iterates its
   ``poolInfo(i)`` entries until it finds the pool whose ``token`` matches
   the queried address.  The corresponding ``lptoken`` is returned as the
   underlying Curve LP.

Both paths price the token 1:1 with the underlying Curve LP.
"""

import logging

import a_sync
from brownie import ZERO_ADDRESS
from eth_typing import ChecksumAddress

from y import ENVIRONMENT_VARIABLES as ENVS
from y import convert
from y._decorators import stuck_coro_debugger
from y.classes.common import ERC20
from y.contracts import Contract, has_methods
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.exceptions import call_reverted
from y.utils.cache import optional_async_diskcache
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)

# Static mapping of known Convex LP tokens → underlying Curve LP tokens.
# These hardcoded entries serve as a fast-path (zero RPC calls) for the most
# commonly encountered tokens.  The dynamic detection path handles any token
# not listed here.
MAPPING = {
    "0x30D9410ED1D5DA1F6C8391af5338C93ab8d4035C": "0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490",  # cvx3crv -> 3crv
    "0xbE0F6478E0E4894CFb14f32855603A083A57c7dA": "0xd632f22692FaC7611d2AA1C0D552930D43CAEd3B",  # cvxFRAX3CRV-f -> FRAX3CRV
    "0xabB54222c2b77158CC975a2b715a3d703c256F05": "0x5a6A4D54456819380173272A5E8E9B9904BdF41B",  # cvxMIM-3LP3CRV-f -> crvMIM
    "0xCA3D9F45FfA69ED454E66539298709cb2dB8cA61": "0x43b4FdFD4Ff969587185cDB6f0BD875c5Fc83f8c",  # cvxalUSD3CRV-f -> crvalusd
    "0xDeFd8FdD20e0f34115C7018CCfb655796F6B2168": "0xc4AD29ba4B3c580e6D59105FFf484999997675Ff",  # cvx3crypto -> 3crypto
}


@a_sync.a_sync(
    default="sync",
    cache_type="memory", ram_cache_maxsize=ENVS.DEFAULT_CACHE_MAXSIZE,
    ram_cache_ttl=5 * 60,
)
@stuck_coro_debugger
@optional_async_diskcache
async def is_convex_lp(token_address: AnyAddressType) -> bool:
    """Determine whether a token is a Convex LP token.

    Detection proceeds in two stages:

    1. **Fast path** – if the address is in the static ``MAPPING``, return ``True``
       immediately without any RPC calls.

    2. **Dynamic path** – for tokens not in the static mapping, call ``operator()``
       on the token and verify the returned address is a Convex booster (has
       ``poolLength()``).

    Args:
        token_address: The address of the token to check.

    Returns:
        ``True`` if the token is a Convex LP token, ``False`` otherwise.

    Examples:
        >>> is_convex_lp("0x30D9410ED1D5DA1F6C8391af5338C93ab8d4035C")
        True

        >>> is_convex_lp("0x0000000000000000000000000000000000000000")
        False
    """
    token_address = await convert.to_address_async(token_address)

    # Fast path: static mapping requires no RPC calls
    if token_address in MAPPING:
        return True

    # Dynamic path: check operator() → booster verification
    lp = await get_underlying_lp(token_address, sync=False)
    return lp is not None


@stuck_coro_debugger
@a_sync.a_sync(
    default="sync",
    cache_type="memory", ram_cache_maxsize=ENVS.DEFAULT_CACHE_MAXSIZE,
    ram_cache_ttl=5 * 60,
)
async def get_underlying_lp(token_address: AnyAddressType) -> ChecksumAddress | None:
    """Return the underlying Curve LP token for a Convex LP token.

    For tokens in the static ``MAPPING``, the result is returned directly.
    Otherwise, the function:

    1. Calls ``operator()`` on the token to obtain the Convex booster address.
    2. Verifies the booster has ``poolLength()`` (confirming it is a Convex booster).
    3. Reads ``poolLength()`` to know the number of pools.
    4. Iterates ``poolInfo(i)`` for each pool until it finds the one whose
       ``token`` (index 1) matches ``token_address``.
    5. Returns the ``lptoken`` (index 0, the underlying Curve LP token).

    Args:
        token_address: The Convex LP token address.

    Returns:
        The underlying Curve LP token address, or ``None`` if not found.

    Examples:
        >>> await get_underlying_lp("0x30D9410ED1D5DA1F6C8391af5338C93ab8d4035C", sync=False)
        '0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490'
    """
    token_address = await convert.to_address_async(token_address)

    # Fast path: static mapping
    if token_address in MAPPING:
        return await convert.to_address_async(MAPPING[token_address])

    # Call operator() to get the booster address
    try:
        booster_address = await raw_call(
            token_address,
            "operator()",
            output="address",
            return_None_on_failure=True,
            sync=False,
        )
    except Exception as e:
        if call_reverted(e):
            return None
        raise

    if not booster_address or booster_address == ZERO_ADDRESS:
        return None

    # Verify the booster looks like a Convex booster (has poolLength())
    if not await has_methods(booster_address, ("poolLength()(uint256)",), sync=False):
        return None

    # Get the number of pools
    try:
        num_pools_raw = await raw_call(
            booster_address,
            "poolLength()",
            output="int",
            return_None_on_failure=True,
            sync=False,
        )
    except Exception as e:
        if call_reverted(e):
            return None
        raise

    if num_pools_raw is None or num_pools_raw == 0:
        return None

    num_pools = int(num_pools_raw)

    # Use Contract object to call poolInfo(uint256) which returns a tuple
    # poolInfo returns: (address lptoken, address token, address gauge,
    #                    address crvRewards, address stash, bool shutdown)
    try:
        booster_contract = await Contract.coroutine(booster_address)
    except Exception:
        return None

    token_address_lower = token_address.lower()
    for i in range(num_pools):
        try:
            pool_info = await booster_contract.poolInfo.coroutine(i)
        except Exception:
            continue

        # pool_info[1] is the token (Convex deposit token / cvxToken)
        if str(pool_info[1]).lower() == token_address_lower:
            lp_token = str(pool_info[0])
            if lp_token and lp_token != ZERO_ADDRESS:
                return await convert.to_address_async(lp_token)
            return None

    return None


@stuck_coro_debugger
@a_sync.a_sync(default="sync")
async def get_price(
    token_address: AnyAddressType,
    block: Block | None = None,
    skip_cache: bool = ENVS.SKIP_CACHE,
) -> UsdPrice:
    """Get the USD price of a Convex LP token.

    Convex LP tokens are priced 1:1 with their underlying Curve LP token.
    The underlying LP address is resolved via :func:`get_underlying_lp`,
    which checks the static mapping first and falls back to dynamic
    ``operator()``-based detection.

    Args:
        token_address: The address of the Convex LP token.
        block: The block number at which to fetch the price. Defaults to the latest block.
        skip_cache: Whether to skip the cache when fetching the price.
            Defaults to :obj:`ENVS.SKIP_CACHE`.

    Returns:
        The USD price of the token (equals the underlying Curve LP price).

    Examples:
        >>> await get_price("0x30D9410ED1D5DA1F6C8391af5338C93ab8d4035C")
        1.23456789

    See Also:
        - :func:`get_underlying_lp` for resolving the underlying LP address.
        - :func:`y.prices.magic.get_price` for the underlying price fetching logic.
    """
    from y.prices import magic

    token_address = await convert.to_address_async(token_address)
    lp_token = await get_underlying_lp(token_address, sync=False)
    return await magic.get_price(lp_token, block, skip_cache=skip_cache, sync=False)
