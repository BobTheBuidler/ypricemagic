import a_sync
import eth_retry
from a_sync.modified import ASyncDecorator
from brownie import chain
from joblib import Memory

from y import ENVIRONMENT_VARIABLES as ENVS


@eth_retry.auto_retry
def _memory():
    return Memory(f"cache/{chain.id}", verbose=0)

memory = _memory()

a_sync_cache: ASyncDecorator = a_sync.a_sync(ram_cache_ttl=ENVS.CACHE_TTL)
