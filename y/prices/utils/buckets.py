from asyncio import as_completed, ensure_future, iscoroutine
from logging import DEBUG, getLogger
from typing import Awaitable, Callable, Tuple

import a_sync

from y import convert
from y.classes.common import ERC20
from y.constants import STABLECOINS
from y.datatypes import Address, AnyAddressType
from y.prices import convex, one_to_one, pendle, popsicle, rkp3r, solidex, yearn
from y.prices.band import band
from y.prices.chainlink import chainlink
from y.prices.dex import mooniswap
from y.prices.dex.balancer import balancer_multiplexer
from y.prices.dex.genericamm import is_generic_amm
from y.prices.dex.uniswap import uniswap_multiplexer
from y.prices.eth_derivs import creth, wsteth
from y.prices.gearbox import gearbox
from y.prices.lending import ib
from y.prices.lending.aave import aave
from y.prices.lending.compound import compound
from y.prices.stable_swap import belt, ellipsis, froyo, mstablefeederpool, saddle
from y.prices.stable_swap.curve import curve
from y.prices.synthetix import synthetix
from y.prices.tokenized_fund import basketdao, gelato, piedao, reserve, tokensets
from y.utils.logging import get_price_logger

logger = getLogger(__name__)


@a_sync.a_sync(default="sync", cache_type="memory")
async def check_bucket(token: AnyAddressType) -> str:
    """Determine and return the category or "bucket" of a given token.

    This function classifies a token by performing a set of tests in the following order:

    1. It first attempts to retrieve a cached bucket from the database via
       :func:`y._db.utils.token.get_bucket`.
    2. Next, it applies simple string-based comparisons defined in the ``string_matchers``
       dictionary.
    3. If no bucket is determined, it concurrently executes a set of asynchronous "calls-only"
       tests for further classification. The function will return immediately once any of these
       tests confirms the token’s membership in a bucket.
    4. If none of the concurrent tests succeed, it falls back to a series of sequential asynchronous
       checks that involve both contract initializations and blockchain calls.

    .. note::
       The fallback sequential tests are executed in order. However, the first two fallback checks
       (for "solidex" and "uni or uni-like lp") are evaluated independently; as a result, if both
       conditions return true, the latter bucket ("uni or uni-like lp") will overwrite the earlier
       assignment from "solidex".

    The final determined bucket is stored in the database using :func:`db.set_bucket`.

    Args:
        token: The token address to classify.

    Examples:
        Basic usage with a stable USD token:
            >>> bucket = check_bucket("0x6B175474E89094C44Da98b954EedeAC495271d0F")
            >>> print(bucket)
            stable usd

        Example triggering a concurrent asynchronous test:
            >>> bucket = check_bucket("0xSomeLPTokenAddress")
            >>> print(bucket)
            popsicle

        Example where multiple fallback conditions are met (note that if both "solidex" and
        "uni or uni-like lp" tests pass, the latter overwrites the former):
            >>> bucket = check_bucket("0xAnotherTokenAddress")
            >>> print(bucket)
            uni or uni-like lp

    See Also:
        :func:`y.convert.to_address_async`
        :func:`y.utils.logging.get_price_logger`
        :func:`_check_bucket_helper` (Helper used for asynchronous bucket checks)
    """
    token_address = await convert.to_address_async(token)
    logger = get_price_logger(token_address, block=None, extra="buckets")

    import y._db.utils.token as db

    bucket = await db.get_bucket(token_address)
    if bucket:
        logger.debug("returning bucket %s from ydb", bucket)
        return bucket

    debug_logs_enabled = logger.isEnabledFor(DEBUG)

    # these require neither calls to the chain nor contract initialization, just string comparisons (pretty sure)
    for bucket, check in string_matchers.items():
        if check(token):
            if debug_logs_enabled:
                await __log_bucket(token_address, bucket)
            db.set_bucket(token_address, bucket)
            return bucket
        elif debug_logs_enabled:
            await __log_not_bucket(token_address, bucket)

    # Check these first, these tests involve asynchronous eth_calls and are launched concurrently.
    futs = [
        ensure_future(_check_bucket_helper(bucket, check, token_address))
        for bucket, check in calls_only.items()
    ]
    for fut in as_completed(futs):
        try:
            bucket, is_member = await fut
        except TypeError:
            raise
        except Exception as e:
            logger.warning(
                "%s when checking %s. This will probably not impact your run.", e, fut
            )
            logger.warning(e, exc_info=True)
            continue

        if is_member:
            if debug_logs_enabled:
                await __log_bucket(token_address, bucket)
            for fut in futs:
                fut.cancel()
            db.set_bucket(token_address, bucket)
            return bucket
        else:
            if debug_logs_enabled:
                await __log_not_bucket(token_address, bucket)
            bucket = None

    # TODO: Refactor the below like the above
    # these require both calls and contract initializations; they are checked sequentially.
    if await solidex.is_solidex_deposit(token_address, sync=False):
        bucket = "solidex"
    if await uniswap_multiplexer.is_uniswap_pool(token_address, sync=False):
        bucket = "uni or uni-like lp"
    elif gearbox and await gearbox.is_diesel_token(token_address, sync=False):
        bucket = "gearbox"

    # this just requires contract initialization but should go behind uniswap
    elif await aave.is_wrapped_atoken_v2(token_address, sync=False):
        bucket = "wrapped atoken v2"
    elif await aave.is_wrapped_atoken_v3(token_address, sync=False):
        bucket = "wrapped atoken v3"
    elif await is_generic_amm(token_address):
        bucket = "generic amm"
    elif await mooniswap.is_mooniswap_pool(token_address, sync=False):
        bucket = "mooniswap lp"
    elif await compound.is_compound_market(token_address, sync=False):
        bucket = "compound"
    elif await _chainlink_and_band(token_address):
        bucket = "chainlink and band"
    elif chainlink and await chainlink.has_feed(token_address, sync=False):
        bucket = "chainlink feed"
    elif synthetix and await synthetix.is_synth(token_address, sync=False):
        bucket = "synthetix"
    elif await yearn.is_yearn_vault(token_address, sync=False):
        bucket = "yearn or yearn-like"
    elif curve and await curve.get_pool(token_address, sync=False):
        bucket = "curve lp"
    if debug_logs_enabled:
        await __log_bucket(token_address, bucket)
    if bucket:
        db.set_bucket(token_address, bucket)
    return bucket


# these require neither calls to the chain nor contract initialization, just string comparisons (pretty sure)
string_matchers = {
    "wrapped gas coin": lambda address: address
    == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
    "stable usd": lambda address: address in STABLECOINS,
    "one to one": one_to_one.is_one_to_one_token,
    "wsteth": wsteth.is_wsteth,
    "creth": creth.is_creth,
    "belt lp": belt.is_belt_lp,
    "froyo": froyo.is_froyo,
    "convex": convex.is_convex_lp,
    "rkp3r": rkp3r.is_rkp3r,
}

# these just require calls
calls_only = {
    "atoken": aave.is_atoken,
    "balancer pool": balancer_multiplexer.is_balancer_pool,
    "ib token": ib.is_ib_token,
    "gelato": gelato.is_gelato_pool,
    "pendle lp": pendle.is_pendle_lp,
    "piedao lp": piedao.is_pie,
    "token set": tokensets.is_token_set,
    "ellipsis lp": ellipsis.is_eps_rewards_pool,
    "mstable feeder pool": mstablefeederpool.is_mstable_feeder_pool,
    "saddle": saddle.is_saddle_lp,
    "basketdao": basketdao.is_basketdao_index,
    "popsicle": popsicle.is_popsicle_lp,
    "reserve": reserve.is_rtoken,
}


async def _chainlink_and_band(token_address) -> bool:
    """
    Check if a token is supported by both Chainlink and Band oracles.

    This function is primarily used for historical data on the Fantom network,
    where Band was used before Chainlink became available.

    Args:
        token_address: The address of the token to check.

    Examples:
        >>> is_supported = await _chainlink_and_band("0x6B175474E89094C44Da98b954EedeAC495271d0F")
        >>> print(is_supported)
        True

    See Also:
        - :func:`y.prices.chainlink.has_feed`
    """
    return (
        chainlink
        and await chainlink.has_feed(token_address, sync=False)
        and token_address in band
    )


async def _check_bucket_helper(
    bucket: str, check: Callable[[Address], Awaitable[bool]], address: Address
) -> Tuple[str, bool]:
    """
    Asynchronously check if a token belongs to a specified bucket.

    This helper function is designed to be executed concurrently as part of the
    "calls-only" checks in :func:`check_bucket`. It invokes a callable that returns
    a boolean indicating whether the token meets the criterion for the specified bucket.
    If the result is not immediately boolean, it awaits the result further.

    Args:
        bucket: The name of the bucket to check.
        check: A callable that checks if the token belongs to the bucket.
        address: The address of the token to check.

    Examples:
        >>> async def dummy_check(addr):
        ...     return addr.startswith("0x")
        >>> result = await _check_bucket_helper("dummy", dummy_check, "0x123")
        >>> print(result)
        ('dummy', True)

    See Also:
        - :func:`check_bucket`
    """
    result = await check(address, sync=False)

    # TODO: debug why we have to re-await sometimes when @optional_async_diskcache is used
    if not isinstance(result, bool):
        if not iscoroutine(result):
            raise TypeError(f"{bucket} result must be boolean. You passed {result}")
        result = await result
    if not isinstance(result, bool):
        # if not iscoroutine(result):
        raise TypeError(f"{bucket} result must be boolean. You passed {result}")
        # result = await result
    return bucket, result


async def __log_bucket(token, bucket):
    symbol = await ERC20(token, asynchronous=True).symbol
    logger._log(DEBUG, "%s %s bucket is %s", (symbol, token, bucket))


async def __log_not_bucket(token, bucket):
    symbol = await ERC20(token, asynchronous=True).symbol
    logger._log(DEBUG, "%s %s bucket is not %s", (symbol, token, bucket))
