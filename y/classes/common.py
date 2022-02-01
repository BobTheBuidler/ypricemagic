
import logging
from functools import cached_property
from typing import Union

import brownie
from y.classes.erc20 import ERC20
from y.decorators import log

logger = logging.getLogger(__name__)

class WeiBalance:
    def __init__(self, balance: int, token: Union[str, brownie.Contract, ERC20], block: int = None) -> None:
        self.balance = balance
        self.token = ERC20(str(token))
        super().__init__()

    def __str__(self) -> str:
        return self.balance

    def __eq__(self, __o: object) -> bool:
        return __o == self.balance
    
    @cached_property
    def readable(self) -> float:
        return self.balance / self.token.scale(block=self.block)
