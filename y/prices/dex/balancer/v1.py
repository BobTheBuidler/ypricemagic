import asyncio
import logging
from contextlib import suppress
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

import a_sync
from a_sync.a_sync import HiddenMethodDescriptor
from brownie import chain
from brownie.convert.datatypes import EthAddress
from brownie.exceptions import VirtualMachineError
from typing_extensions import Self
from web3.exceptions import ContractLogicError

from y import ENVIRONMENT_VARIABLES as ENVS
from y._decorators import stuck_coro_debugger
from y.classes.common import ERC20
from y.constants import dai, usdc, wbtc, weth
from y.contracts import Contract, contract_creation_block_async
from y.datatypes import (Address, AddressOrContract, AnyAddressType, Block,
                         Pool, UsdPrice, UsdValue)
from y.networks import Network
from y.prices import magic
from y.prices.dex.balancer._abc import BalancerABC, BalancerPool
from y.utils.cache import optional_async_diskcache

EXCHANGE_PROXY = {
    Network.Mainnet: '0x3E66B66Fd1d0b02fDa6C811Da9E0547970DB2f21',
}.get(chain.id)

SCALES_TO_TRY = [1.0, 0.5, 0.1]
TOKENOUTS_TO_TRY = [weth, dai, usdc, wbtc]

logger = logging.getLogger(__name__)

async def _calc_out_value(token_out: AddressOrContract, total_outout: int, scale: float, block: int, skip_cache: bool = ENVS.SKIP_CACHE) -> float:
    out_scale, out_price = await asyncio.gather(ERC20(token_out, asynchronous=True).scale, magic.get_price(token_out, block, skip_cache=skip_cache, sync=False))
    return (total_outout / out_scale) * float(out_price) / scale

class BalancerV1Pool(BalancerPool):
    @a_sync.aka.cached_property
    @stuck_coro_debugger
    @optional_async_diskcache
    async def tokens(self) -> List[ERC20]:
        contract = await Contract.coroutine(self.address)
        return [ERC20(token, asynchronous=self.asynchronous) for token in await contract.getFinalTokens]
    __tokens__: HiddenMethodDescriptor[Self, List[ERC20]]

    @stuck_coro_debugger
    async def get_tvl(self, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> Optional[UsdValue]:
        token_balances = await self.get_balances(block=block, sync=False)
        good_balances = {
            token: balance
            for token, balance
            in token_balances.items()
            if await token.price(block=block, return_None_on_failure=True, skip_cache=skip_cache, sync=False) is not None
        }
        
        prices = await ERC20.price.map(good_balances, block=block, return_None_on_failure=True, skip_cache=skip_cache).values()

        # in case we couldn't get prices for all tokens, we can extrapolate from the prices we did get
        good_value = sum(balance * Decimal(price) for balance, price in zip(good_balances.values(),prices))
        if len(good_balances):
            return good_value / len(good_balances) * len(token_balances)
        return None
    
    @stuck_coro_debugger
    async def get_balances(self, block: Optional[Block] = None) -> Dict[ERC20, Decimal]:
        return await a_sync.map(self.get_balance, self.__tokens__, block=block or 'latest')

    @stuck_coro_debugger
    async def get_balance(self, token: AnyAddressType, block: Block) -> Decimal:
        balance, scale = await asyncio.gather(
            self.check_liquidity(str(token), block, sync=False),
            ERC20(token, asynchronous=True).scale,
        )
        return Decimal(balance) / scale

    @stuck_coro_debugger
    @a_sync.a_sync(ram_cache_maxsize=10_000, ram_cache_ttl=10*60)
    async def check_liquidity(self, token: Address, block: Block) -> int:
        if block < await self.deploy_block(sync=False):
            return 0
        contract = await Contract.coroutine(self.address)
        return await contract.getBalance.coroutine(token, block_identifier=block)
    

class BalancerV1(BalancerABC[BalancerV1Pool]):

    _pool_type = BalancerV1Pool

    _check_methods = ("getCurrentTokens()(address[])", "getTotalDenormalizedWeight()(uint)", "totalSupply()(uint)")

    def __init__(self, asynchronous: bool = False) -> None:
        self.asynchronous = asynchronous
        self.exchange_proxy = Contract(EXCHANGE_PROXY) if EXCHANGE_PROXY else None
    
    @stuck_coro_debugger
    async def get_token_price(self, token_address: AddressOrContract, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> Optional[UsdPrice]:
        if block is not None and block < await contract_creation_block_async(self.exchange_proxy, True):
            return None
        for scale in SCALES_TO_TRY:
            # Can we get an output if we try smaller size? try consecutively smaller
            if output := await self.get_some_output(token_address, block=block, scale=scale, sync=False):
                return await _calc_out_value(*output, scale, block=block, skip_cache=skip_cache)
    
    @stuck_coro_debugger
    async def check_liquidity_against(
        self,
        token_in: AddressOrContract,
        token_out: AddressOrContract,
        scale: int = 1,
        block: Optional[Block] = None
        ) -> Optional[int]:

        amount_in = await ERC20(token_in, asynchronous=True).scale * scale
        with suppress(ValueError, VirtualMachineError, ContractLogicError):
            # across various dep versions we get these various excs
            view_split_exact_in = await self.exchange_proxy.viewSplitExactIn.coroutine(
                token_in,
                token_out,
                amount_in,
                32, # NOTE: 32 is max
                block_identifier = block,
            )
            return view_split_exact_in['totalOutput']
    
    @stuck_coro_debugger
    async def get_some_output(
        self,
        token_in: AddressOrContract,
        scale: int = 1,
        block: Optional[Block] = None
        ) -> Optional[Tuple[EthAddress,int]]:
        for token_out in TOKENOUTS_TO_TRY:
            if output := await self.check_liquidity_against(token_in, token_out, block=block, scale=scale, sync=False):
                return token_out, output

    @stuck_coro_debugger
    async def check_liquidity(self, token: Address, block: Block, ignore_pools: Tuple[Pool, ...] = ()) -> int:
        pools = []
        pools = [pool for pool in pools if pool not in ignore_pools]
        return await BalancerV1Pool.check_liquidity.max(pools, token=token, block=block, sync=False) if pools else 0
