import logging
from functools import lru_cache

from y.constants import usdc
from y.contracts import Contract, has_methods
from y.decorators import log

logger = logging.getLogger(__name__)

@log(logger)
@lru_cache
def is_token_set(address):
    return has_methods(address, {"tokenIsComponent(address)(bool)", "getComponents()(address[])", "naturalUnit()(uint)"})

@log(logger)
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
