import eth_retry
from brownie import chain
from joblib import Memory


@eth_retry.auto_retry
def _memory():
    return Memory(f"cache/{chain.id}", verbose=0)

memory = _memory()
