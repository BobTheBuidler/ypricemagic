import logging

from brownie import web3
from cachetools.func import lru_cache

logger = logging.getLogger(__name__)

@lru_cache(1)
def get_ethereum_client():
    client = web3.clientVersion
    if client.startswith('TurboGeth'):
        return 'tg'
    if client.lower().startswith('erigon'):
        return 'erigon'
    if client.lower().startswith('geth'):
        return 'geth'
    logger.debug(f"client: {client}")
    return client
