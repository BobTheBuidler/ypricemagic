import logging

from async_lru import alru_cache
from brownie import web3
from cachetools.func import lru_cache

from y.utils.dank_mids import dank_w3
from y.utils.logging import yLazyLogger

logger = logging.getLogger(__name__)

@lru_cache(1)
@yLazyLogger(logger)
def get_ethereum_client() -> str:
    return _get_ethereum_client(web3.clientVersion)

@alru_cache(maxsize=1, cache_exceptions=False)
async def get_ethereum_client_async() -> str:
    return _get_ethereum_client(await dank_w3.clientVersion)

@yLazyLogger(logger)
def _get_ethereum_client(client: str) -> str:
    if client.startswith('TurboGeth'):
        return 'tg'
    if client.lower().startswith('erigon'):
        return 'erigon'
    if client.lower().startswith('geth'):
        return 'geth'
    logger.debug(f"client: {client}")
