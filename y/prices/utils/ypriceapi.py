
import asyncio
import logging
import os
from http import HTTPStatus
from time import time
from typing import Callable, Optional

from aiohttp import BasicAuth, ClientResponse, ClientSession, TCPConnector
from aiohttp.client_exceptions import ClientError
from async_lru import alru_cache
from brownie import chain

from y.classes.common import UsdPrice
from y.datatypes import Address, Block
from y.utils.dank_mids import dank_w3

logger = logging.getLogger(__name__)

# current
YPRICEAPI_URL = os.environ.get("YPRICEAPI_URL")
USE_YPRICEAPI = bool(YPRICEAPI_URL)
YPRICEAPI_SIGNER = os.environ.get("YPRICEAPI_SIGNER")
YPRICEAPI_SIGNATURE = os.environ.get("YPRICEAPI_SIGNATURE")
auth_headers = {"X-Signer": YPRICEAPI_SIGNER, "X-Signature": YPRICEAPI_SIGNATURE} if YPRICEAPI_SIGNER and YPRICEAPI_SIGNATURE else {}

# old
YPRICEAPI_USER = os.environ.get("YPRICEAPI_USER")
YPRICEAPI_PASS = os.environ.get("YPRICEAPI_PASS")
old_auth = BasicAuth(YPRICEAPI_USER, YPRICEAPI_PASS) if YPRICEAPI_USER and YPRICEAPI_PASS else None

ONE_MINUTE = 60  # some arbitrary amount of time in case the header is missing on unexpected 5xx responses
FALLBACK_STR = "Falling back to your node for pricing."
YPRICEAPI_SEMAPHORE = asyncio.Semaphore(int(os.environ.get("YPRICEAPI_SEMAPHORE", 100)))

notified = set()
resume_at = 0
get_retry_header: Callable[[ClientResponse], int] = lambda x: int(x.headers.get("Retry-After", ONE_MINUTE))


# NOTE: if you want to bypass ypriceapi for specific tokens, have your program add the addresses to this set.
skip_ypriceapi = set()

@alru_cache(maxsize=1)
async def get_session() -> ClientSession:
    return ClientSession(YPRICEAPI_URL, connector=TCPConnector(verify_ssl=False), headers=auth_headers)

async def get_price_from_api(
    token: Address,
    block: Optional[Block]
) -> Optional[UsdPrice]:
    
    if token in skip_ypriceapi:
        return None

    # Notify user if using old auth scheme
    if old_auth is not None:
        raise NotImplementedError("YPRICEAPI_USER and YPRICEAPI_PASS are no longer used.\nPlease sign up for a plan (we have a free tier) at ypriceapi-beta.yearn.finance.\nThen, pass in YPRICEAPI_SIGNER (the wallet you used to sign up) and YPRICEAPI_SIGNATURE (the signature you generated on the website) env vars to continue using ypriceAPI.")

    if USE_YPRICEAPI is False or not auth_headers:
        logger.error('You are unable to get price from the ypriceAPI unless you pass YPRICEAPI_URL, YPRICEAPI_SIGNER, and YPRICEAPI_SIGNATURE env vars.')
        return None

    if block is None:
        block = await dank_w3.eth.block_number

    if time() < resume_at:
        # NOTE: The reason we are here has already been logged.
        return None

    async with YPRICEAPI_SEMAPHORE:
        try:
            session = await get_session()
            response = await session.get(f'/get_price/{chain.id}/{token}?block={block}')
            return await read_response(token, block, response)
        except asyncio.TimeoutError:
            logger.warning(f'ypriceAPI timed out for {token} at {block}.{FALLBACK_STR}')
        except ClientError as e:
            logger.warning(f'ypriceAPI {e.__class__.__name__} for {token} at {block}.{FALLBACK_STR}')


async def read_response(token: Address, block: Optional[Block], response: ClientResponse) -> Optional[UsdPrice]:
    # 200
    if response.status == HTTPStatus.OK:
        return await response.json()

    # 401
    elif response.status == HTTPStatus.UNAUTHORIZED:
        if HTTPStatus.UNAUTHORIZED not in notified:
            logger.error(f'Your provided ypriceAPI credentials are not authorized for use.{FALLBACK_STR}')
            notified.add(HTTPStatus.UNAUTHORIZED)
                
    # 404
    elif response.status == HTTPStatus.NOT_FOUND:
        logger.debug(f"Failed to get price from API: {token} at {block}")


    # Server Errors
    
    # 502
    elif response.status == HTTPStatus.BAD_GATEWAY:
        logger.warning(f"ypriceAPI returned status code {_get_err_reason(response)}:")
        try:
            logger.warning(await response.json(content_type=None) or await response.text())
        except Exception:
            logger.warning(f'exception decoding ypriceapi 502 response.{FALLBACK_STR}', exc_info=True)
        _set_resume_at(get_retry_header(response))
    
    # 503
    elif response.status == HTTPStatus.SERVICE_UNAVAILABLE:
        logger.warning(f"ypriceAPI returned status code {_get_err_reason(response)}:")
        try:
            logger.warning(await response.json(content_type=None) or await response.text())
        except Exception:
            logger.warning(f'exception decoding ypriceapi 503 response.{FALLBACK_STR}', exc_info=True)
        _set_resume_at(get_retry_header(response))

    else:
        logger.warning(f'ypriceAPI returned status code {_get_err_reason(response)} for {token} at {block}.{FALLBACK_STR}')
            

def _get_err_reason(response: ClientResponse) -> str:
    if response.reason is None:
        return f"[{response.status}]"
    ascii_encodable_reason = response.reason.encode(
        "ascii", "backslashreplace"
    ).decode("ascii")
    return f"[{response.status} {ascii_encodable_reason}]"
    
def _set_resume_at(retry_after: float) -> None:
    global resume_at
    logger.info(f"Falling back to your node for {retry_after/60} minutes.")
    resume_from_this_err_at = time() + retry_after
    if resume_from_this_err_at > resume_at:
        resume_at = resume_from_this_err_at