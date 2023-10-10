import asyncio
import logging
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

import a_sync
from brownie import chain
from brownie.convert.datatypes import EthAddress
from brownie.exceptions import VirtualMachineError

from y.classes.common import ERC20
from y.constants import dai, usdc, wbtc, weth
from y.contracts import Contract, contract_creation_block_async, has_methods
from y.datatypes import (Address, AddressOrContract, AnyAddressType, Block,
                         Pool, UsdPrice, UsdValue)
from y.decorators import stuck_coro_debugger
from y.networks import Network
from y.prices import magic

EXCHANGE_PROXY = {
    Network.Mainnet: '0x3E66B66Fd1d0b02fDa6C811Da9E0547970DB2f21',
}.get(chain.id, None)

logger = logging.getLogger(__name__)

async def _calc_out_value(token_out: AddressOrContract, total_outout: int, scale: float, block) -> float:
    out_scale, out_price = await asyncio.gather(ERC20(token_out, asynchronous=True).scale, magic.get_price(token_out, block, sync=False))
    return (total_outout / out_scale) * float(out_price) / scale

class BalancerV1Pool(ERC20):
    async def tokens(self, block: Optional[Block] = None) -> List[ERC20]:
        tokens = await self.contract.getCurrentTokens.coroutine(block_identifier=block)
        return [ERC20(token, asynchronous=self.asynchronous) for token in tokens]
    
    @stuck_coro_debugger
    async def get_pool_price(self, block: Optional[Block] = None) -> UsdPrice:
        supply = await self.total_supply_readable(block=block, sync=False)
        if supply == 0:
            return 0
        return UsdPrice(await self.get_tvl(block=block, sync=False) / Decimal(supply))

    @stuck_coro_debugger
    async def get_tvl(self, block: Optional[Block] = None) -> Optional[UsdValue]:
        token_balances = await self.get_balances(block=block, sync=False)
        good_balances = {
            token: balance
            for token, balance
            in token_balances.items()
            if await token.price(block=block, return_None_on_failure=True, sync=False) is not None
        }
        
        prices = await asyncio.gather(*[token.price(block=block, return_None_on_failure = True, sync=False) for token in good_balances])

        # in case we couldn't get prices for all tokens, we can extrapolate from the prices we did get
        good_value = sum(balance * Decimal(price) for balance, price in zip(good_balances.values(),prices))
        if len(good_balances):
            return good_value / len(good_balances) * len(token_balances)
        return None
    
    @stuck_coro_debugger
    async def get_balances(self, block: Optional[Block] = None) -> Dict[ERC20, Decimal]:
        tokens = await self.tokens(block=block, sync=False)
        balances = await asyncio.gather(*[self.get_balance(token, block or 'latest', sync=False) for token in tokens])
        return dict(zip(tokens, balances))

    @stuck_coro_debugger
    async def get_balance(self, token: AnyAddressType, block: Block) -> Decimal:
        balance, scale = await asyncio.gather(
            self.check_liquidity(str(token), block, sync=False),
            ERC20(token, asynchronous=True).scale,
        )
        return Decimal(balance) / scale

    @a_sync.a_sync(ram_cache_maxsize=10_000, ram_cache_ttl=10*60)
    @stuck_coro_debugger
    async def check_liquidity(self, token: Address, block: Block) -> int:
        if block < await self.deploy_block(sync=False):
            return 0
        return await self.contract.getBalance.coroutine(token, block_identifier=block)
    

class BalancerV1(a_sync.ASyncGenericSingleton):
    def __init__(self, asynchronous: bool = False) -> None:
        self.asynchronous = asynchronous
        self.exchange_proxy = Contract(EXCHANGE_PROXY) if EXCHANGE_PROXY else None
    
    def __str__(self) -> str:
        return "BalancerV1()"
    
    def __repr__(self) -> str:
        return "<BalancerV1>"
    
    @stuck_coro_debugger
    async def is_pool(self, token_address: AnyAddressType) -> bool:
        return await has_methods(token_address ,("getCurrentTokens()(address[])", "getTotalDenormalizedWeight()(uint)", "totalSupply()(uint)"), sync=False)

    @stuck_coro_debugger
    async def get_pool_price(self, token_address: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
        assert await self.is_pool(token_address, sync=False)
        return await BalancerV1Pool(token_address, asynchronous=True).get_pool_price(block=block)
    
    @stuck_coro_debugger
    async def get_token_price(self, token_address: AddressOrContract, block: Optional[Block] = None) -> Optional[UsdPrice]:
        if block is not None and block < await contract_creation_block_async(self.exchange_proxy, True):
            return None
        scale = 1.0
        out, totalOutput = await self.get_some_output(token_address, block=block, sync=False)
        if out:
            return await _calc_out_value(out, totalOutput, scale, block=block)
        # Can we get an output if we try smaller size?
        scale = 0.5
        out, totalOutput = await self.get_some_output(token_address, block=block, scale=scale, sync=False) 
        if out:
            return await _calc_out_value(out, totalOutput, scale, block=block)
        # How about now? 
        scale = 0.1
        out, totalOutput = await self.get_some_output(token_address, block=block, scale=scale, sync=False)
        if out:
            return await _calc_out_value(out, totalOutput, scale, block=block)
        return None
    
    @stuck_coro_debugger
    async def check_liquidity_against(
        self,
        token_in: AddressOrContract,
        token_out: AddressOrContract,
        scale: int = 1,
        block: Optional[Block] = None
        ) -> Tuple[EthAddress, int]:

        amount_in = await ERC20(token_in, asynchronous=True).scale * scale
        view_split_exact_in = await self.exchange_proxy.viewSplitExactIn.coroutine(
            token_in,
            token_out,
            amount_in,
            32, # NOTE: 32 is max
            block_identifier = block,
        )

        output = view_split_exact_in['totalOutput']

        return token_out, output
    
    @stuck_coro_debugger
    async def get_some_output(
        self,
        token_in: AddressOrContract,
        scale: int = 1,
        block: Optional[Block] = None
        ) -> Tuple[EthAddress,int]:

        try:
            out, totalOutput = await self.check_liquidity_against(token_in, weth, block=block, sync=False)
        except (ValueError, VirtualMachineError):
            try:
                out, totalOutput = await self.check_liquidity_against(token_in, dai, block=block, sync=False)
            except (ValueError, VirtualMachineError):
                try:
                    out, totalOutput = await self.check_liquidity_against(token_in, usdc, block=block, sync=False)
                except (ValueError, VirtualMachineError):
                    try:
                        out, totalOutput = await self.check_liquidity_against(token_in, wbtc, block=block, sync=False)
                    except (ValueError, VirtualMachineError):
                        out = None
                        totalOutput = None
        return out, totalOutput

    @stuck_coro_debugger
    async def check_liquidity(self, token: Address, block: Block, ignore_pools: Tuple[Pool, ...] = ()) -> int:
        pools = []
        pools = [pool for pool in pools if pool not in ignore_pools]
        return max(await asyncio.gather(*[pool.check_liquidity(token, block, sync=False) for pool in pools])) if pools else 0
