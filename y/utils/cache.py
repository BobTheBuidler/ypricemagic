from brownie import chain
from joblib import Memory
from y.decorators import auto_retry


@auto_retry
def _memory():
    return Memory(f"cache/{chain.id}", verbose=0)

memory = _memory()
