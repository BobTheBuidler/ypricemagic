
# sourcery skip: merge-assign-and-aug-assign
import asyncio
import logging
import os
from collections import defaultdict
from http import HTTPStatus
from random import randint
from time import time
from typing import Any, Callable, List, Optional

from aiohttp import BasicAuth, ClientResponse, ClientSession, TCPConnector
from aiohttp.client_exceptions import ClientError, ContentTypeError
from async_lru import alru_cache
from brownie import chain

from y import constants
from y.classes.common import UsdPrice
from y.datatypes import Address, Block
from y.utils.dank_mids import dank_w3

logger = logging.getLogger(__name__)

# current
header_env_names = {"X-Signer": "YPRICEAPI_SIGNER", "X-Signature": "YPRICEAPI_SIGNATURE"}
AUTH_HEADERS = {header: os.environ.get(env) for header, env in header_env_names.items()}
AUTH_HEADERS_PRESENT = all(AUTH_HEADERS.values())

# old
YPRICEAPI_USER = os.environ.get("YPRICEAPI_USER")
YPRICEAPI_PASS = os.environ.get("YPRICEAPI_PASS")
OLD_AUTH = BasicAuth(YPRICEAPI_USER, YPRICEAPI_PASS) if YPRICEAPI_USER and YPRICEAPI_PASS else None

ONE_MINUTE = 60  # some arbitrary amount of time in case the header is missing on unexpected 5xx responses
FALLBACK_STR = "Falling back to your node for pricing."
YPRICEAPI_SEMAPHORE = asyncio.Semaphore(int(os.environ.get("YPRICEAPI_SEMAPHORE", 100)))

if any(AUTH_HEADERS.values()) and not AUTH_HEADERS_PRESENT:
    for header in AUTH_HEADERS:
        if not AUTH_HEADERS[header]:
            raise EnvironmentError(f'You must also pass in a value for {header_env_names[header]} in order to use ypriceAPI.')
                
should_use = not constants.SKIP_YPRICEAPI 
notified = set()
auth_notifs = defaultdict(int)
resume_at = 0
get_retry_header: Callable[[ClientResponse], int] = lambda x: int(x.headers.get("Retry-After", ONE_MINUTE))

# NOTE: if you want to bypass ypriceapi for specific tokens, have your program add the addresses to this set.
skip_tokens = set()
skip_ypriceapi = skip_tokens  # alias for backward compatability

#########################
# YPRICEAPI PUBLIC BETA #
#########################
    
_you_get = [
    "access to your desired price data more quickly...",
    "...from nodes run by yearn-affiliated big brains...",
    "on all the networks "
]
_testimonials = [
    "I can now get prices for all of my useless shitcoins without waiting all day for ypricemagic to load logs."
    "I don't need to maintain an archive node anymore and that's saving me money.", 
    "Wow, so fast!",
]
beta_announcement = "ypriceAPI is now in beta!\n\n"
beta_announcement += "Head to ypriceapi-beta.yearn.finance and sign up for access. You get:\n"
for you_get in _you_get:
    beta_announcement += f" - {you_get}\n"
beta_announcement += "\nCheck out some testimonials from our close frens:"
for testimonial in _testimonials:
    beta_announcement += f' - from anon{randint(0, 9999)}, "{testimonial}"\n'

def announce_beta() -> None:
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
    pass

@alru_cache(maxsize=1)
async def get_session() -> ClientSession:
    return ClientSession("https://ypriceapi-beta.yearn.finance", connector=TCPConnector(verify_ssl=False), headers=AUTH_HEADERS)

# TODO: Fix
#@alru_cache(maxsize=1, ttl=ONE_MINUTE * 60)
#async def get_chains() -> List[int]:
#    session = await get_session()
#    response = await session.get("/chains")
#    chains = await read_response(response)
#    return [] if chains is None else list(chains.keys())

async def get_price(
    token: Address,
    block: Optional[Block]
) -> Optional[UsdPrice]:
    
    if not AUTH_HEADERS_PRESENT:
        announce_beta()
        return None
        
    if time() < resume_at:
        # NOTE: The reason we are here has already been logged.
        return None

    if block is None:
        block = await dank_w3.eth.block_number

    async with YPRICEAPI_SEMAPHORE:
        try:
            #if chain.id not in await get_chains():
            #    return None
            session = await get_session()
            response = await session.get(f'/get_price/{chain.id}/{token}?block={block}')
            return await read_response(response, token, block)
        except asyncio.TimeoutError:
            logger.warning(f'ypriceAPI timed out for {token} at {block}.{FALLBACK_STR}')
        except ClientError as e:
            logger.warning(f'ypriceAPI {e.__class__.__name__} for {token} at {block}.{FALLBACK_STR}')

async def read_response(response: ClientResponse, token: Optional[Address] = None, block: Optional[Block] = None) -> Optional[Any]:
    
    # 200
    if response.status == HTTPStatus.OK:
        try:
            return await response.json()
        except ContentTypeError as e:
            response = await response.json(content_type=None)
            if response:
                raise BadResponse(response) from e
            logger.warning(f'ypriceAPI returned status code {_get_err_reason(response)} with response None. Must investigate.')

    # 401
    elif response.status == HTTPStatus.UNAUTHORIZED:
        if HTTPStatus.UNAUTHORIZED not in notified:
            logger.error(f'Your provided ypriceAPI credentials are not authorized for use.{FALLBACK_STR}')
            notified.add(HTTPStatus.UNAUTHORIZED)
            
    # 404
    elif response.status == HTTPStatus.NOT_FOUND and token and block:
        logger.debug(f"Failed to get price from API: {token} at {block}")

    # Server Errors
    
    # 502 & 503
    elif response.status in {HTTPStatus.BAD_GATEWAY, HTTPStatus.SERVICE_UNAVAILABLE}:
        logger.warning(f"ypriceAPI returned status code {_get_err_reason(response)}")
        try:
            msg = await response.json(content_type=None) or await response.text()
        except Exception:
            logger.warning(f'exception decoding ypriceapi {response.status} response.{FALLBACK_STR}', exc_info=True)
            msg = ''
        if msg:
            logger.warning(msg)
        _set_resume_at(get_retry_header(response))

    else:
        msg = f'ypriceAPI returned status code {_get_err_reason(response)}'
        if token and block:
            msg += f' for {token} at {block}.{FALLBACK_STR}'
        logger.warning(msg)
            

def _get_err_reason(response: ClientResponse) -> str:
    if response.reason is None:
        return f"[{response.status}]"
    ascii_encodable_reason = response.reason.encode(
        "ascii", "backslashreplace"
    ).decode("ascii")
    return f"[{response.status} {ascii_encodable_reason}]"
    
def _set_resume_at(retry_after: float) -> None:
    global resume_at
    logger.info(f"Falling back to your node for {int(retry_after/60)} minutes.")
    resume_from_this_err_at = time() + retry_after
    if resume_from_this_err_at > resume_at:
        resume_at = resume_from_this_err_at