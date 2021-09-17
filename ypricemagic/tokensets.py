from brownie import Contract
from . import magic
from .constants import usdc
import logging

def is_token_set(address):
    pool = Contract(address)
    required = {"tokenIsComponent", "getComponents", "naturalUnit"}
    return set(pool.__dict__) & required == required

def get_price(token, block=None):
    setValuer = Contract('0xDdF4F0775fF69c73619a4dBB42Ba61b0ac1F555f')
    try:
        return setValuer.calculateSetTokenValuation(token, usdc, block_identifier=block)

    except ValueError: # NOTE: This will run for v1 token sets
        set = Contract(token)
        components = set.getComponents(block_identifier = block)
        balances = zip(components,set.getUnits(block_identifier = block))
        logging.debug(f"set balances: {balances}")
        return None