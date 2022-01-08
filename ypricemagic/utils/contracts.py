import logging

from brownie import Contract, chain, web3
from ypricemagic.interfaces.ERC20 import ERC20ABI
from ypricemagic.utils.cache import memory

logger = logging.getLogger(__name__)


def Contract_erc20(address):
    return Contract.from_abi('ERC20',address,ERC20ABI)


def Contract_with_erc20_fallback(address):
    try:
        contract = Contract(address)
    except (AttributeError, ValueError, IndexError):
        contract = Contract_erc20(address)
    return contract


@memory.cache()
def contract_creation_block(address) -> int:
    """
    Determine the block when a contract was created using binary search.
    NOTE Requires access to historical state. Doesn't account for CREATE2 or SELFDESTRUCT.
    """
    logger.info("contract creation block %s", address)
    height = chain.height
    lo, hi = 0, height
    while hi - lo > 1:
        mid = lo + (hi - lo) // 2
        if web3.eth.get_code(address, block_identifier=mid):
            hi = mid
        else:
            lo = mid
    return hi if hi != height else None
