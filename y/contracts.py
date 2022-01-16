import logging
import threading
from functools import lru_cache

from brownie import Contract as _Contract
from brownie import chain, web3
from brownie.exceptions import CompilerError
from y.utils.cache import memory
from ypricemagic.interfaces.ERC20 import ERC20ABI

logger = logging.getLogger(__name__)


def Contract_erc20(address):
    return _Contract.from_abi('ERC20',address,ERC20ABI)


def Contract_with_erc20_fallback(address):
    try:
        contract = _Contract(address)
    except (AttributeError, CompilerError, IndexError, ValueError):
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
        try:
            if web3.eth.get_code(address, block_identifier=mid): hi = mid
            else: lo = mid
        except ValueError as e:
            if 'missing trie node' in str(e):
                logger.critical('missing trie node, `contract_creation_block` may output a higher block than actual. Please try again using an archive node.')
                lo = mid
            else: raise
    return hi if hi != height else None

class Singleton(type):
    def __init__(self, *args, **kwargs):
        self.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            self.__instance = super().__call__(*args, **kwargs)
            return self.__instance
        else:
            return self.__instance

# cached Contract instance, saves about 20ms of init time
_contract_lock = threading.Lock()
_contract = lru_cache(maxsize=None)(_Contract)

def Contract(address):
    with _contract_lock:
        return _contract(address)

def is_contract(address: str) -> bool:
    '''checks to see if the input address is a contract'''
    return web3.eth.get_code(address) != '0x'
