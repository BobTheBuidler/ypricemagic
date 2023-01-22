
import asyncio
import logging
import os
from typing import Optional

from aiohttp import BasicAuth, ClientSession, TCPConnector, ClientResponse
from brownie import chain

from y.classes.common import UsdPrice
from y.datatypes import Address, Block
from y.utils.dank_mids import dank_w3

logger = logging.getLogger(__name__)


YPRICEAPI_USER = os.environ.get("YPRICEAPI_USER")
YPRICEAPI_PASS = os.environ.get("YPRICEAPI_PASS")
YPRICEAPI_URL = os.environ.get("YPRICEAPI_URL")

USE_YPRICEAPI = bool(YPRICEAPI_URL)

notified = set()

auth = BasicAuth(YPRICEAPI_USER, YPRICEAPI_PASS) if YPRICEAPI_USER and YPRICEAPI_PASS else None

ypriceapi_semaphore = asyncio.Semaphore(50)

fallback_str = "Falling back to your node for pricing."

async def get_price_from_api(
    token: Address,
    block: Optional[Block]
) -> Optional[UsdPrice]:

    if not YPRICEAPI_URL or auth is None:
        logger.error('You are unable to get price from the ypriceAPI unless you pass YPRICEAPI_URL, YPRICEAPI_USER, and YPRICEAPI_PASS.')
        return None
    
    if block is None:
        block = await dank_w3.eth.block_number
    
    async with ypriceapi_semaphore:
        try:
            async with ClientSession(YPRICEAPI_URL, connector=TCPConnector(verify_ssl=False), auth=auth) as session:
                response = await session.get(f'/get_price/{chain.id}/{token}/{block}')

                # Handle successful response
                if response.status == 200:
                    result = await response.json()
                    if isinstance(result, str):
                        logger.warning(f"Failed to get price from API: {result}")
                        return None
                    else:
                        return result

                # Handle unsuccessful response
                # Unauthorized
                elif response.status == 401:
                    if 401 not in notified:
                        logger.error('Your provided ypriceAPI credentials are not authorized for use.' + fallback_str)
                        notified.add(401)
                    return None
        
                else:
                    logger.warning(f'ypriceAPI returned status code {_get_err_reason(response)} for {token} at {block}.' + fallback_str)
                    
        except asyncio.TimeoutError:
            logger.warning(f'ypriceAPI timed out for {token} at {block}.' + fallback_str)
            

def _get_err_reason(response: ClientResponse) -> str:
    if response.reason is None:
        return f"[{response.status}]"
    ascii_encodable_reason = response.reason.encode(
        "ascii", "backslashreplace"
    ).decode("ascii")
    return f"[{response.status} {ascii_encodable_reason}]"
    