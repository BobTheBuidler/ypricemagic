import logging

from brownie import web3
from cachetools.func import lru_cache
from y.utils.logging import yLazyLogger

logger = logging.getLogger(__name__)

@yLazyLogger(logger)
@lru_cache(1)
def get_ethereum_client() -> str:
    client = web3.clientVersion
    if client.startswith('TurboGeth'):
        return 'tg'
    if client.lower().startswith('erigon'):
        return 'erigon'
    if client.lower().startswith('geth'):
        return 'geth'
    logger.debug(f"client: {client}")
    return client
