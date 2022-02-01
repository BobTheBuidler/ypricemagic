
import logging
from functools import lru_cache

from brownie import convert
from decorators import log
from y.erc20 import decimals, totalSupply
from ypricemagic import magic

logger = logging.getLogger(__name__)

class ERC20:
    def __init__(self, address: str) -> None:
        self.address = convert.to_address(address)
        pass

    @log(logger)
    @lru_cache
    def decimals(self, block: int = None) -> int:
        return decimals(self.address, block=block)
    
    @log(logger)
    def scale(self, block: int = None) -> int:
        return 10 ** self.decimals(block=block)

    @log(logger)
    @lru_cache
    def total_supply(self, block: int = None) -> int:
        return totalSupply(self.address, block=block)
    
    @log(logger)
    def total_supply_readable(self, block: int = None) -> float:
        return self.total_supply(block=block) / self.scale(block=block)

    @log(logger)
    def price(self, block: int = None, return_None_on_failure: bool = False) -> float:
        return magic.get_price(
            self.address, 
            block=block, 
            fail_to_None=return_None_on_failure
        )
