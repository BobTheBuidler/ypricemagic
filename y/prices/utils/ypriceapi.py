
import logging
import os

from aiohttp import ClientSession, TCPConnector, BasicAuth
from y.utils.dank_mids import dank_w3
from y.datatypes import Address,Block
from brownie import chain
from typing import Optional
from y.classes.common import UsdPrice

logger = logging.getLogger(__name__)


YPRICEAPI_USER = os.environ.get("YPRICEAPI_USER")
YPRICEAPI_PASS = os.environ.get("YPRICEAPI_PASS")
YPRICEAPI_URL = os.environ.get("YPRICEAPI_URL")

USE_YPRICEAPI = bool(YPRICEAPI_URL)

notified = set()

auth = BasicAuth(YPRICEAPI_USER, YPRICEAPI_PASS) if YPRICEAPI_USER and YPRICEAPI_PASS else None

async def get_price_from_api(
    token: Address,
    block: Optional[Block]
) -> Optional[UsdPrice]:

    if not YPRICEAPI_URL or auth is None:
        logger.error('You are unable to get price from the ypriceAPI unless you pass YPRICEAPI_URL, YPRICEAPI_USER, and YPRICEAPI_PASS.')
        return None
    
    if block is None:
        block = await dank_w3.eth.block_number

    async with ClientSession(YPRICEAPI_URL, connector=TCPConnector(verify_ssl=False), auth=auth) as session:
        response = await session.get(f'/get_price/{chain.id}/{token}/{block}')

        # Handle successful response
        if response.status == 200:
            result = await response.json()
            if isinstance(result, str):
                logger.error(f"Failed to get price from API: {result}")
                return None
            else:
                return result

        # Handle unsuccessful response
        # Unauthorized
        elif response.status == 401:
            if 401 not in notified:
                logger.error('Your provided ypriceAPI user and password pair is not authorized for use. Falling back to your own node for pricing.')
                notified.add(401)
            return None
        
        else:
            raise NotImplementedError(f"status code {response.status} is not yet handled. Please tell Bob to fix this.")
            