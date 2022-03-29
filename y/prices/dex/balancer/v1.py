import logging
from typing import Dict, List, Optional, Tuple

from brownie import chain
from brownie.convert.datatypes import EthAddress
from y.classes.common import ERC20
from y.classes.singleton import Singleton
from y.constants import dai, usdc, wbtc, weth
from y.contracts import Contract, has_methods
from y.datatypes import UsdPrice, UsdValue
from y.decorators import log
from y.networks import Network
from y.prices import magic
from y.typing import AddressOrContract, AnyAddressType, Block
from y.utils.multicall import fetch_multicall, multicall_decimals
from y.utils.raw_calls import _decimals

EXCHANGE_PROXY = {
    Network.Mainnet: '0x3E66B66Fd1d0b02fDa6C811Da9E0547970DB2f21',
}.get(chain.id, None)

logger = logging.getLogger(__name__)


class BalancerV1Pool(ERC20):
    def __init__(self, pool_address: AnyAddressType) -> None:
        super().__init__(pool_address)

    @log(logger)
    def tokens(self, block: Optional[Block] = None) -> List[ERC20]:
        tokens = self.contract.getCurrentTokens(block_identifier=block)
        return [ERC20(token) for token in tokens]

    @log(logger)
    def get_pool_price(self, block: Optional[Block] = None) -> UsdPrice:
        supply = self.total_supply_readable(block=block)
        if supply == 0:
            return 0
        return UsdPrice(self.get_tvl(block=block) / supply)

    @log(logger)
    def get_tvl(self, block: Optional[Block] = None) -> Optional[UsdValue]:
        token_balances = self.get_balances()
        good_balances = {
            token: balance
            for token, balance
            in token_balances.items()
            if token.price(block=block, return_None_on_failure=True) is not None
        }
        
        # in case we couldn't get prices for all tokens, we can extrapolate from the prices we did get
        good_value = sum(balance * token.price(block=block, return_None_on_failure=True) for token, balance in good_balances.items())
        if len(good_balances):
            return good_value / len(good_balances) * len(token_balances)
        return None

    @log(logger)
    def get_balances(self, block: Optional[Block] = None) -> Dict[ERC20, float]:
        tokens = self.tokens(block=block)
        balances = fetch_multicall(*[[self.contract, "getBalance", token] for token in tokens], block=block)
        balances = [balance if balance else 0 for balance in balances]
        decimals = multicall_decimals(tokens, block)
        return {token:balance / 10 ** decimal for token, balance, decimal in zip(tokens,balances,decimals)}


class BalancerV1(metaclass=Singleton):
    def __init__(self) -> None:
        self.exchange_proxy = Contract(EXCHANGE_PROXY) if EXCHANGE_PROXY else None
    
    def __str__(self) -> str:
        return "BalancerV1()"
    
    @log(logger)
    def is_pool(self, token_address: AnyAddressType) -> bool:
        return has_methods(token_address ,{"getCurrentTokens()(address[])", "getTotalDenormalizedWeight()(uint)", "totalSupply()(uint)"})
    
    @log(logger)
    def get_pool_price(self, token_address: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
        assert self.is_pool(token_address)
        return BalancerV1Pool(token_address).get_pool_price(block=block)

    @log(logger)
    def get_token_price(self, token_address: AddressOrContract, block: Optional[Block] = None) -> UsdPrice:
        out, totalOutput = self.get_some_output(token_address, block=block)
        if out:
            return (totalOutput / 10 ** _decimals(out,block)) * magic.get_price(out, block)
        # Can we get an output if we try smaller size?
        scale = 0.5
        out, totalOutput = self.get_some_output(token_address, block=block, scale=scale) 
        if out:
            return (totalOutput / 10 ** _decimals(out,block)) * magic.get_price(out, block) / scale
        # How about now? 
        scale = 0.1
        out, totalOutput = self.get_some_output(token_address, block=block, scale=scale)
        if out:
            return (totalOutput / 10 ** _decimals(out,block)) * magic.get_price(out, block) / scale
        else:
            return

    @log(logger)
    def check_liquidity_against(
        self,
        token_in: AddressOrContract,
        token_out: AddressOrContract,
        scale: int = 1,
        block: Optional[Block] = None
        ) -> Tuple[EthAddress, int]:
        output = self.exchange_proxy.viewSplitExactIn(
            token_in, token_out, 10 ** _decimals(token_in) * scale, 32 # NOTE: 32 is max
            , block_identifier = block
        )['totalOutput']
        return token_out, output

    @log(logger)
    def get_some_output(
        self,
        token_in: AddressOrContract,
        scale: int = 1,
        block: Optional[Block] = None
        ) -> Tuple[EthAddress,int]:
        try:
            out, totalOutput = self.check_liquidity_against(token_in, weth, block=block)
        except ValueError:
            try:
                out, totalOutput = self.check_liquidity_against(token_in, dai, block=block)
            except ValueError:
                try:
                    out, totalOutput = self.check_liquidity_against(token_in, usdc, block=block)
                except ValueError:
                    try:
                        out, totalOutput = self.check_liquidity_against(token_in, wbtc, block=block)
                    except ValueError:
                        out = None
                        totalOutput = None
        return out, totalOutput
