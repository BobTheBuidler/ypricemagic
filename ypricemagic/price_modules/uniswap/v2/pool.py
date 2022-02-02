
import logging
from functools import cached_property
from typing import Tuple

from brownie import web3
from multicall import Call, Multicall
from y.classes.common import WeiBalance
from y.classes.erc20 import ERC20
from y.contracts import Contract
from y.decorators import log
from y.exceptions import (ContractNotVerified, MessedUpBrownieContract,
                          NonStandardERC20, NotAUniswapV2Pool, call_reverted)
from ypricemagic.utils.multicall import fetch_multicall
from ypricemagic.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)


class UniswapPoolV2(ERC20):
    def __init__(self, address: str) -> None:
        super().__init__(address)
        try: self.decimals
        except NonStandardERC20: raise NotAUniswapV2Pool        
    
    @cached_property
    @log(logger)
    def factory(self) -> str:
        try: return raw_call(self.address, 'factory()', output='address')
        except ValueError as e:
            if call_reverted(e): raise NotAUniswapV2Pool
            # `is not a valid ETH address` means we got some kind of response from the chain.
            # but couldn't convert to address. If it happens to be a goofy but
            # verified uni fork, maybe we can get factory this way
            okay_errors = ['is not a valid ETH address','invalid opcode','invalid jump destination']
            if any([msg in str(e) for msg in okay_errors]):
                try: self.factory = Contract(self.address).factory()
                except AttributeError: raise NotAUniswapV2Pool
            else: raise

    @cached_property
    @log(logger)
    def tokens(self) -> Tuple[ERC20, ERC20]:
        token0, token1, supply, reserves = self.get_pool_details()
        return ERC20(token0), ERC20(token1)
    
    @log(logger)
    def token0(self) -> ERC20:
        return self.tokens[0]

    @log(logger)
    def token1(self) -> ERC20:
        return self.tokens[1]
    
    @log(logger)
    def get_price(self, block: int = None) -> float:
        return self.tvl(block=block) / self.total_supply_readable(block=block)
    
    @log(logger)
    def reserves(self, block: int = None) -> Tuple[WeiBalance, WeiBalance]:
        token0, token1, total_supply, reserves = self.get_pool_details(block)
        return (WeiBalance(reserve, token, block=block) for reserve, token in zip(reserves, self.tokens))

    @log(logger)
    def tvl(self, block: int = None) -> float:
        prices = [token.price(block=block, return_None_on_failure=True) for token in self.tokens]
        vals = [None if price is None else reserve.readable * price for reserve, price in zip(self.reserves(block=block), prices)]
        if not vals[0] or not vals[1]: vals = _extrapolate_value(vals)
        return sum(vals)

    @log(logger)
    def get_pool_details(self, block: int = None) -> Tuple[str, str, int, Tuple[int, int, int]]:
        methods = 'token0()(address)', 'token1()(address)', 'totalSupply()(uint)', 'getReserves()((uint112,uint112,uint32))'
        calls = [Call(self.address, [method], [[method, None]]) for method in methods]
        try: token0, token1, supply, reserves = Multicall(calls, _w3=web3, block_id=block)().values()
        except Exception as e:
            if not call_reverted(e): raise
            # if call reverted, let's try with brownie. Sometimes this works, not sure why
            try:
                contract = Contract(self.address)
                token0, token1, supply, reserves = fetch_multicall([contract,'token0'],[contract,'token1'],[contract,'totalSupply'],[contract,'getReserves'],block=block)
            except (ContractNotVerified, MessedUpBrownieContract):
                raise NotAUniswapV2Pool(self.address, "Are you sure this is a uni pool?")
        return token0, token1, supply, reserves

@log(logger)
def _extrapolate_value(vals: Tuple[float, float]) -> Tuple[float, float]:
    if vals[0] and not vals[1]: vals[1] = vals[0]
    if vals[1] and not vals[0]: vals[0] = vals[1]
    return vals
