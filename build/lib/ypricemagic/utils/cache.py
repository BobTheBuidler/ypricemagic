from joblib import Memory
from brownie import chain

memory = Memory(f"cache/{chain.id}", verbose=0)
