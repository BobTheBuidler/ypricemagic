import logging
from typing import Dict, List, Optional, Tuple

from brownie import chain
from brownie.convert.datatypes import EthAddress
from brownie.exceptions import VirtualMachineError
from multicall.utils import await_awaitable, gather
from y.classes.common import ERC20
from y.classes.singleton import Singleton
from y.constants import dai, usdc, wbtc, weth
from y.contracts import Contract, has_methods_async
from y.datatypes import (AddressOrContract, AnyAddressType, Block, UsdPrice,
                         UsdValue)
from y.networks import Network
from y.prices import magic
from y.utils.logging import yLazyLogger
from y.utils.multicall import fetch_multicall, multicall_decimals_async

EXCHANGE_PROXY = {
    Network.Mainnet: '0x3E66B66Fd1d0b02fDa6C811Da9E0547970DB2f21',
}.get(chain.id, None)

logger = logging.getLogger(__name__)

async def _calc_out_value(token_out: AddressOrContract, total_outout: int, scale: float, block) -> float:
    out_scale, out_price = await gather([
        ERC20(token_out).scale,
        magic.get_price_async(token_out, block),
    ])
    return (total_outout / out_scale) * out_price / scale

class BalancerV1Pool(ERC20):
    def __init__(self, pool_address: AnyAddressType) -> None:
        super().__init__(pool_address)

    @yLazyLogger(logger)
    def tokens(self, block: Optional[Block] = None) -> List[ERC20]:
        tokens = self.contract.getCurrentTokens(block_identifier=block)
        return [ERC20(token) for token in tokens]

    @yLazyLogger(logger)
    def get_pool_price(self, block: Optional[Block] = None) -> UsdPrice:
        return await_awaitable(self.get_pool_price_async(block=block))

    @yLazyLogger(logger)
    async def get_pool_price_async(self, block: Optional[Block] = None) -> UsdPrice:
        supply = await self.total_supply_readable_async(block=block)
        if supply == 0:
            return 0
        return UsdPrice(await self.get_tvl_async(block=block) / supply)

    @yLazyLogger(logger)
    def get_tvl(self, block: Optional[Block] = None) -> Optional[UsdValue]:
        return await_awaitable(self.get_tvl_async(block=block))

    @yLazyLogger(logger)
    async def get_tvl_async(self, block: Optional[Block] = None) -> Optional[UsdValue]:
        token_balances = await self.get_balances_async()
        good_balances = {
            token: balance
            for token, balance
            in token_balances.items()
            if await token.price_async(block=block, return_None_on_failure=True) is not None
        }
        
        prices = await gather([
            token.price_async(block=block, return_None_on_failure = True)
            for token in good_balances.keys()
        ])

        # in case we couldn't get prices for all tokens, we can extrapolate from the prices we did get
        good_value = sum(balance * price for balance, price in zip(good_balances.values(),prices))
        if len(good_balances):
            return good_value / len(good_balances) * len(token_balances)
        return None

    @yLazyLogger(logger)
    def get_balances(self, block: Optional[Block] = None) -> Dict[ERC20, float]:
        return await_awaitable(self.get_balances_async(block=block))
    
    @yLazyLogger(logger)
    async def get_balances_async(self, block: Optional[Block] = None) -> Dict[ERC20, float]:
        tokens = self.tokens(block=block)
        balances = fetch_multicall(*[[self.contract, "getBalance", token] for token in tokens], block=block)
        balances = [balance if balance else 0 for balance in balances]
        decimals = await multicall_decimals_async(tokens, block)
        return {token:balance / 10 ** decimal for token, balance, decimal in zip(tokens,balances,decimals)}


class BalancerV1(metaclass=Singleton):
    def __init__(self) -> None:
        self.exchange_proxy = Contract(EXCHANGE_PROXY) if EXCHANGE_PROXY else None
    
    def __str__(self) -> str:
        return "BalancerV1()"
    
    def __repr__(self) -> str:
        return "<BalancerV1>"
    
    @yLazyLogger(logger)
    def is_pool(self, token_address: AnyAddressType) -> bool:
        return await_awaitable(self.is_pool_async(token_address))
    
    @yLazyLogger(logger)
    async def is_pool_async(self, token_address: AnyAddressType) -> bool:
        return await has_methods_async(token_address ,("getCurrentTokens()(address[])", "getTotalDenormalizedWeight()(uint)", "totalSupply()(uint)"))
    
    @yLazyLogger(logger)
    def get_pool_price(self, token_address: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
        return await_awaitable(self.get_pool_price_async(token_address, block=block))

    @yLazyLogger(logger)
    async def get_pool_price_async(self, token_address: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
        assert await self.is_pool_async(token_address)
        return await BalancerV1Pool(token_address).get_pool_price_async(block=block)

    @yLazyLogger(logger)
    def get_token_price(self, token_address: AddressOrContract, block: Optional[Block] = None) -> UsdPrice:
        return await_awaitable(self.get_token_price_async(token_address, block=block))
    
    @yLazyLogger(logger)
    async def get_token_price_async(self, token_address: AddressOrContract, block: Optional[Block] = None) -> UsdPrice:
        scale = 1.0
        out, totalOutput = await self.get_some_output_async(token_address, block=block)
        if out:
            return await _calc_out_value(out, totalOutput, scale, block=block)
        # Can we get an output if we try smaller size?
        scale = 0.5
        out, totalOutput = await self.get_some_output_async(token_address, block=block, scale=scale) 
        if out:
            return await _calc_out_value(out, totalOutput, scale, block=block)
        # How about now? 
        scale = 0.1
        out, totalOutput = await self.get_some_output_async(token_address, block=block, scale=scale)
        if out:
            return await _calc_out_value(out, totalOutput, scale, block=block)
        else:
            return

    @yLazyLogger(logger)
    def check_liquidity_against(
        self,
        token_in: AddressOrContract,
        token_out: AddressOrContract,
        scale: int = 1,
        block: Optional[Block] = None
        ) -> Tuple[EthAddress, int]:

        return await_awaitable(
            self.check_liquidity_against_async(token_in, token_out, scale=scale, block=block)
        )
    
    @yLazyLogger(logger)
    async def check_liquidity_against_async(
        self,
        token_in: AddressOrContract,
        token_out: AddressOrContract,
        scale: int = 1,
        block: Optional[Block] = None
        ) -> Tuple[EthAddress, int]:

        amount_in = await ERC20(token_in).scale * scale
        view_split_exact_in = await self.exchange_proxy.viewSplitExactIn.coroutine(
            token_in,
            token_out,
            amount_in,
            32, # NOTE: 32 is max
            block_identifier = block,
        )

        output = view_split_exact_in['totalOutput']

        return token_out, output

    @yLazyLogger(logger)
    def get_some_output(
        self,
        token_in: AddressOrContract,
        scale: int = 1,
        block: Optional[Block] = None
        ) -> Tuple[EthAddress,int]:

        return await_awaitable(self.get_some_output_async(token_in, scale=scale, block=block))
    
    @yLazyLogger(logger)
    async def get_some_output_async(
        self,
        token_in: AddressOrContract,
        scale: int = 1,
        block: Optional[Block] = None
        ) -> Tuple[EthAddress,int]:

        try:
            out, totalOutput = await self.check_liquidity_against_async(token_in, weth, block=block)
        except (ValueError, VirtualMachineError):
            try:
                out, totalOutput = await self.check_liquidity_against_async(token_in, dai, block=block)
            except (ValueError, VirtualMachineError):
                try:
                    out, totalOutput = await self.check_liquidity_against_async(token_in, usdc, block=block)
                except (ValueError, VirtualMachineError):
                    try:
                        out, totalOutput = await self.check_liquidity_against_async(token_in, wbtc, block=block)
                    except (ValueError, VirtualMachineError):
                        out = None
                        totalOutput = None
        return out, totalOutput
