# sourcery skip: merge-assign-and-aug-assign
import asyncio
import logging
import os
from collections import defaultdict
from http import HTTPStatus
from random import randint
from time import time
from typing import Any, Callable, Dict, Optional

import dank_mids
from aiohttp import (
    BasicAuth,
    ClientResponse,
    ClientSession,
    ClientTimeout,
    TCPConnector,
)
from aiohttp.client_exceptions import (
    ClientConnectorSSLError,
    ClientError,
    ContentTypeError,
)
from async_lru import alru_cache

from y import ENVIRONMENT_VARIABLES as ENVS
from y.classes.common import UsdPrice
from y.constants import CHAINID
from y.datatypes import Address, Block
from y.networks import Network

logger = logging.getLogger(__name__)

# current
header_env_names = {
    "X-Signer": "YPRICEAPI_SIGNER",
    "X-Signature": "YPRICEAPI_SIGNATURE",
}
AUTH_HEADERS = {header: os.environ.get(env) for header, env in header_env_names.items()}
AUTH_HEADERS_PRESENT = all(AUTH_HEADERS.values())

# old
YPRICEAPI_USER = os.environ.get("YPRICEAPI_USER")
YPRICEAPI_PASS = os.environ.get("YPRICEAPI_PASS")
OLD_AUTH = (
    BasicAuth(YPRICEAPI_USER, YPRICEAPI_PASS)
    if YPRICEAPI_USER and YPRICEAPI_PASS
    else None
)

ONE_MINUTE = 60  # some arbitrary amount of time in case the header is missing on unexpected 5xx responses
ONE_HOUR = ONE_MINUTE * 60
FALLBACK_STR = "Falling back to your node for pricing."

YPRICEAPI_TIMEOUT = ClientTimeout(
    int(os.environ.get("YPRICEAPI_TIMEOUT", 5 * ONE_MINUTE))
)  # Five minutes is the default timeout from aiohttp.
YPRICEAPI_SEMAPHORE = dank_mids.BlockSemaphore(
    int(os.environ.get("YPRICEAPI_SEMAPHORE", 100))
)

if any(AUTH_HEADERS.values()) and not AUTH_HEADERS_PRESENT:
    for header in AUTH_HEADERS:
        if not AUTH_HEADERS[header]:
            raise EnvironmentError(
                f"You must also pass in a value for {header_env_names[header]} in order to use ypriceAPI."
            )

should_use = not ENVS.SKIP_YPRICEAPI
notified = set()
auth_notifs = defaultdict(int)
resume_at = 0
get_retry_header: Callable[[ClientResponse], int] = lambda x: int(
    x.headers.get("Retry-After", ONE_MINUTE)
)

# NOTE: if you want to bypass ypriceapi for specific tokens, have your program add the addresses to this set.
skip_tokens = set()
skip_ypriceapi = skip_tokens  # alias for backward compatability

#########################
# YPRICEAPI PUBLIC BETA #
#########################

_you_get = [
    "access to your desired price data more quickly...",
    "...from nodes run by yearn-affiliated big brains...",
    "...on all the networks Yearn supports.",
]
_testimonials = [
    "I can now get prices for all of my useless shitcoins without waiting all day for ypricemagic to load logs.",
    "I don't need to maintain an archive node anymore and that's saving me money.",
    "Wow, so fast!",
]
beta_announcement = "ypriceAPI is now in beta!\n\n"
beta_announcement += (
    "Head to ypriceapi-beta.yearn.finance and sign up for access. You get:\n"
)
for you_get in _you_get:
    beta_announcement += f" - {you_get}\n"
beta_announcement += "\nCheck out some testimonials from our close frens:\n"
for testimonial in _testimonials:
    beta_announcement += f' - from anon{randint(0, 9999)}, "{testimonial}"\n'


def announce_beta() -> None:
    """Announce the beta version of ypriceAPI.

    This function logs the beta announcement message, which includes
    information about the benefits of using ypriceAPI and testimonials
    from users.

    Examples:
        >>> announce_beta()
        ypriceAPI is now in beta!
        ...
    """
    spam_your_logs_fn = logger.info if logger.isEnabledFor(logging.INFO) else print
    spam_your_logs_fn(beta_announcement)
    global should_use
    should_use = False


# TODO: Remove this when enough time has passed.
# Notify user if using old auth scheme
if OLD_AUTH is not None:
    announce_beta()
    raise NotImplementedError(
        "YPRICEAPI_USER and YPRICEAPI_PASS are no longer used.\n"
        + "Please sign up for a plan (we have a free tier) at ypriceapi-beta.yearn.finance.\n"
        + "Then, pass in the following env vars to continue using ypriceAPI:\n"
        + " - YPRICEAPI_SIGNATURE, the signature you generated on the website"
        + " - YPRICEAPI_SIGNER, the wallet you used to sign up\n"
        + "You can unset the old envs to continue using ypricemagic."
    )


class BadResponse(Exception):
    """Exception raised for bad responses from ypriceAPI."""


@alru_cache(maxsize=1)
async def get_session() -> ClientSession:
    """Get an aiohttp ClientSession for ypriceAPI.

    This session is configured with the ypriceAPI URL, headers, and timeout.

    Returns:
        An aiohttp ClientSession object.

    Examples:
        >>> session = await get_session()
    """
    return ClientSession(
        os.environ.get("YPRICEAPI_URL", "https://ypriceapi-beta.yearn.finance"),
        connector=TCPConnector(verify_ssl=False),
        headers=AUTH_HEADERS,
        timeout=YPRICEAPI_TIMEOUT,
    )


@alru_cache(ttl=ONE_HOUR)
async def get_chains() -> Dict[int, str]:
    """Get the supported chains from ypriceAPI.

    Returns:
        A dictionary mapping chain IDs to chain names.

    Examples:
        >>> chains = await get_chains()
        >>> chains[1]
        'Ethereum Mainnet'
    """
    session = await get_session()
    async with session.get("/chains") as response:
        chains = await read_response(response) or {}
    return {int(k): v for k, v in chains.items()}


@alru_cache(ttl=ONE_HOUR)
async def chain_supported(chainid: int) -> bool:
    """Check if a chain is supported by ypriceAPI.

    Args:
        chainid: The chain ID to check.

    Returns:
        True if the chain is supported, False otherwise.

    Examples:
        >>> await chain_supported(1)
        True
        >>> await chain_supported(9999)
        False

    See Also:
        :func:`get_chains` for retrieving the list of supported chains.
    """
    if chainid in await get_chains():
        return True
    logger.info("ypriceAPI does not support %s at this time.", Network.name())
    return False


async def get_price(token: Address, block: Optional[Block]) -> Optional[UsdPrice]:
    """Get the price of a token from ypriceAPI.

    Args:
        token: The address of the token.
        block: The block number to query.

    Returns:
        The price of the token in USD as an instance of :class:`UsdPrice`, or None if the price cannot be retrieved.

    This function will return None if the authorization headers are not present or if the current time is less than the resume time.

    Examples:
        >>> price = await get_price("0xTokenAddress", 12345678)
        >>> print(price)
        $1234.56780000

    Raises:
        ClientConnectorSSLError: If there is an SSL error during the request.
        asyncio.TimeoutError: If the request times out.
        ClientError: If there is a client error during the request.

    See Also:
        :class:`UsdPrice` for the price representation.
    """
    if not AUTH_HEADERS_PRESENT:
        announce_beta()
        return None

    if time() < resume_at:
        # NOTE: The reason we are here has already been logged.
        return None

    if block is None:
        block = await dank_mids.eth.block_number

    async with YPRICEAPI_SEMAPHORE[block]:
        try:
            tries = 0
            while True:
                try:
                    if not await chain_supported(CHAINID):
                        return None
                    session = await get_session()
                    async with session.get(
                        f"/get_price/{CHAINID}/{token}?block={block}"
                    ) as response:
                        return (
                            UsdPrice(price)
                            if (price := await read_response(response, token, block))
                            else None
                        )
                except ClientConnectorSSLError as e:
                    if (
                        "[[SSL: TLSV1_ALERT_INTERNAL_ERROR] tlsv1 alert internal error (_ssl.c:1129)]"
                        not in str(e)
                        or tries >= 50
                    ):
                        raise
                    tries += 1
        except asyncio.TimeoutError:
            logger.warning(f"ypriceAPI timed out for {token} at {block}.{FALLBACK_STR}")
        except ContentTypeError:
            raise
        except ClientError as e:
            logger.warning(
                f"ypriceAPI {e.__class__.__name__} for {token} at {block}.{FALLBACK_STR}"
            )


async def read_response(
    response: ClientResponse,
    token: Optional[Address] = None,
    block: Optional[Block] = None,
) -> Optional[Any]:
    """Read and process the response from ypriceAPI.

    Args:
        response: The aiohttp ClientResponse object.
        token: The token address (optional).
        block: The block number (optional).

    Returns:
        The parsed response data, or None if the response is not valid.

    Raises:
        BadResponse: If the response content type is invalid.

    Examples:
        >>> response = await session.get("/get_price/1/0xTokenAddress?block=12345678")
        >>> data = await read_response(response)
    """
    # 200
    if response.status == HTTPStatus.OK:
        try:
            return await response.json()
        except ContentTypeError as e:
            msg = await response.json(content_type=None)
            if msg:
                raise BadResponse(msg) from e
            logger.warning(
                f"ypriceAPI returned status code {_get_err_reason(response)} with response None. Must investigate."
            )

    # 401
    elif response.status == HTTPStatus.UNAUTHORIZED:
        if HTTPStatus.UNAUTHORIZED not in notified:
            logger.error(
                f"Your provided ypriceAPI credentials are not authorized for use.{FALLBACK_STR}"
            )
            notified.add(HTTPStatus.UNAUTHORIZED)

    # 404
    elif response.status == HTTPStatus.NOT_FOUND and token and block:
        logger.debug("Failed to get price from API: %s at %s", token, block)

    # Server Errors

    # 502 & 503
    elif response.status in {HTTPStatus.BAD_GATEWAY, HTTPStatus.SERVICE_UNAVAILABLE}:
        logger.warning("ypriceAPI returned status code %s", _get_err_reason(response))
        try:
            msg = await response.json(content_type=None) or await response.text()
        except Exception:
            logger.warning(
                "exception decoding ypriceapi %s response.%s",
                response.status,
                FALLBACK_STR,
                exc_info=True,
            )
            msg = ""
        if msg:
            logger.warning(msg)
        _set_resume_at(get_retry_header(response))

    else:
        msg = f"ypriceAPI returned status code {_get_err_reason(response)}"
        if token and block:
            msg += f" for {token} at {block}.{FALLBACK_STR}"
        logger.warning(msg)


def _get_err_reason(response: ClientResponse) -> str:
    """Get the error reason from a ClientResponse.

    Args:
        response: The aiohttp ClientResponse object.

    Returns:
        A string representing the error reason.

    Examples:
        >>> reason = _get_err_reason(response)
        >>> print(reason)
        [404 Not Found]
    """
    if response.reason is None:
        return f"[{response.status}]"
    ascii_encodable_reason = response.reason.encode("ascii", "backslashreplace").decode(
        "ascii"
    )
    return f"[{response.status} {ascii_encodable_reason}]"


def _set_resume_at(retry_after: float) -> None:
    """Set the resume time for ypriceAPI requests.

    Args:
        retry_after: The time to wait before retrying, in seconds.

    Examples:
        >>> _set_resume_at(60)
    """
    global resume_at
    logger.info("Falling back to your node for %s minutes.", int(retry_after / 60))
    resume_from_this_err_at = time() + retry_after
    if resume_from_this_err_at > resume_at:
        resume_at = resume_from_this_err_at
