import logging
from contextlib import suppress
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

import a_sync
from a_sync import cgather
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
from y.datatypes import (
    Address,
    AddressOrContract,
    AnyAddressType,
    Block,
    Pool,
    UsdPrice,
    UsdValue,
)
from y.exceptions import continue_if_call_reverted
from y.networks import Network
from y.prices import magic
from y.prices.dex.balancer._abc import BalancerABC, BalancerPool
from y.utils.cache import optional_async_diskcache

EXCHANGE_PROXY = {
    Network.Mainnet: "0x3E66B66Fd1d0b02fDa6C811Da9E0547970DB2f21",
}.get(chain.id)

SCALES_TO_TRY = [1.0, 0.5, 0.1]
TOKENOUTS_TO_TRY = [weth, dai, usdc, wbtc]

logger = logging.getLogger(__name__)


async def _calc_out_value(
    token_out: AddressOrContract,
    total_outout: int,
    scale: float,
    block: int,
    skip_cache: bool = ENVS.SKIP_CACHE,
) -> float:
    """Calculate the output value for a given token.

    Args:
        token_out: The output token address or contract.
        total_outout: The total output amount.
        scale: The scale factor.
        block: The block number.
        skip_cache: Whether to skip the cache.

    Returns:
        The calculated output value.

    Examples:
        >>> await _calc_out_value(weth, 1000, 1.0, 12345678)
        0.5

    See Also:
        - :func:`y.prices.magic.get_price`
    """
    out_scale, out_price = await cgather(
        ERC20._get_scale_for(token_out),
        magic.get_price(token_out, block, skip_cache=skip_cache, sync=False),
    )
    return (total_outout / out_scale) * float(out_price) / scale


class BalancerV1Pool(BalancerPool):
    """A Balancer V1 Pool."""

    @a_sync.aka.cached_property
    @stuck_coro_debugger
    # @optional_async_diskcache
    async def tokens(self) -> List[ERC20]:
        """Get the list of tokens in the pool.

        Returns:
            A list of :class:`~y.classes.common.ERC20` tokens in the pool.

        Examples:
            >>> pool = BalancerV1Pool("0x1234567890abcdef1234567890abcdef12345678")
            >>> await pool.tokens
            [<ERC20 TKN '0x1234567890abcdef1234567890abcdef12345678'>, ...]

        See Also:
            - :class:`~y.classes.common.ERC20`
        """
        contract = await Contract.coroutine(self.address)
        return [
            ERC20(token, asynchronous=self.asynchronous)
            for token in await contract.getFinalTokens
        ]

    __tokens__: HiddenMethodDescriptor[Self, List[ERC20]]

    @stuck_coro_debugger
    async def get_tvl(
        self, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE
    ) -> Optional[UsdValue]:
        """Get the total value locked (TVL) in the pool.

        Args:
            block: The block number to query.
            skip_cache: Whether to skip the cache.

        Returns:
            The total value locked in the pool, or None if it cannot be determined.

        Examples:
            >>> pool = BalancerV1Pool("0x1234567890abcdef1234567890abcdef12345678")
            >>> await pool.get_tvl()
            123456.78

        See Also:
            - :class:`~y.datatypes.UsdValue`
        """
        token_balances = await self.get_balances(block=block, sync=False)
        good_balances = {
            token: balance
            for token, balance in token_balances.items()
            if await token.price(
                block=block,
                return_None_on_failure=True,
                skip_cache=skip_cache,
                sync=False,
            )
            is not None
        }

        if not good_balances:
            return None

        prices = await ERC20.price.map(
            good_balances,
            block=block,
            return_None_on_failure=True,
            skip_cache=skip_cache,
        ).values()

        # in case we couldn't get prices for all tokens, we can extrapolate from the prices we did get
        good_value = sum(
            balance * Decimal(price)
            for balance, price in zip(good_balances.values(), prices)
        )

        return good_value / len(good_balances) * len(token_balances)

    @stuck_coro_debugger
    async def get_balances(self, block: Optional[Block] = None) -> Dict[ERC20, Decimal]:
        """Get the balances of tokens in the pool.

        Args:
            block: The block number to query.

        Returns:
            A dictionary mapping :class:`~y.classes.common.ERC20` tokens to their balances.

        Examples:
            >>> pool = BalancerV1Pool("0x1234567890abcdef1234567890abcdef12345678")
            >>> await pool.get_balances()
            {<ERC20 TKN '0x1234567890abcdef1234567890abcdef12345678'>: Decimal('1000'), ...}

        See Also:
            - :class:`~y.classes.common.ERC20`
        """
        return await a_sync.map(
            self.get_balance, self.__tokens__, block=block or "latest"
        )

    @stuck_coro_debugger
    async def get_balance(self, token: AnyAddressType, block: Block) -> Decimal:
        """Get the balance of a specific token in the pool.

        Args:
            token: The token address.
            block: The block number to query.

        Returns:
            The balance of the token in the pool.

        Examples:
            >>> pool = BalancerV1Pool("0x1234567890abcdef1234567890abcdef12345678")
            >>> await pool.get_balance("0xabcdefabcdefabcdefabcdefabcdefabcdef")
            Decimal('1000')
        """
        balance, scale = await cgather(
            self.check_liquidity(str(token), block, sync=False),
            ERC20._get_scale_for(token),
        )
        return Decimal(balance) / scale

    @stuck_coro_debugger
    @a_sync.a_sync(ram_cache_maxsize=10_000, ram_cache_ttl=10 * 60)
    async def check_liquidity(self, token: Address, block: Block) -> int:
        """Check the liquidity of a specific token in the pool.

        Args:
            token: The token address.
            block: The block number to query.

        Returns:
            The liquidity of the token in the pool.

        Examples:
            >>> pool = BalancerV1Pool("0x1234567890abcdef1234567890abcdef12345678")
            >>> await pool.check_liquidity("0xabcdefabcdefabcdefabcdefabcdefabcdef")
            1000
        """
        if block < await self.deploy_block(sync=False):
            return 0
        contract = await Contract.coroutine(self.address)
        try:
            return await contract.getBalance.coroutine(token, block_identifier=block)
        except Exception as e:
            # the pool was not yet finalized at this block
            # NOTE: does this happen for any pool except YLA? tbd...
            if "NOT_BOUND" in str(e):
                return 0
            elif e.args and str(e.args[0]) == "execution reverted":
                # we only want to continue on exact match of the original (no extra context added) exception
                return 0
            raise


class BalancerV1(BalancerABC[BalancerV1Pool]):
    """A Balancer V1 instance."""

    _pool_type = BalancerV1Pool

    _check_methods = (
        "getCurrentTokens()(address[])",
        "getTotalDenormalizedWeight()(uint)",
        "totalSupply()(uint)",
    )

    def __init__(self, *, asynchronous: bool = False) -> None:
        """Initialize a BalancerV1 instance.

        Args:
            asynchronous: Whether to use asynchronous operations.

        Examples:
            >>> balancer = BalancerV1(asynchronous=True)
        """
        super().__init__()
        self.asynchronous = asynchronous
        self.exchange_proxy = Contract(EXCHANGE_PROXY) if EXCHANGE_PROXY else None

    @stuck_coro_debugger
    async def get_token_price(
        self,
        token_address: AddressOrContract,
        block: Optional[Block] = None,
        skip_cache: bool = ENVS.SKIP_CACHE,
    ) -> Optional[UsdPrice]:
        """Get the price of a token in the pool.

        Args:
            token_address: The token address or contract.
            block: The block number to query.
            skip_cache: Whether to skip the cache.

        Returns:
            The price of the token in USD, or None if it cannot be determined.

        Examples:
            >>> balancer = BalancerV1(asynchronous=True)
            >>> await balancer.get_token_price("0xabcdefabcdefabcdefabcdefabcdefabcdef")
            1.23

        See Also:
            - :class:`~y.datatypes.UsdPrice`
        """
        if block is not None and block < await contract_creation_block_async(
            self.exchange_proxy, True
        ):
            return None
        for scale in SCALES_TO_TRY:
            # Can we get an output if we try smaller size? try consecutively smaller
            if output := await self.get_some_output(
                token_address, block=block, scale=scale, sync=False
            ):
                return await _calc_out_value(
                    *output, scale, block=block, skip_cache=skip_cache
                )

    @stuck_coro_debugger
    async def check_liquidity_against(
        self,
        token_in: AddressOrContract,
        token_out: AddressOrContract,
        scale: int = 1,
        block: Optional[Block] = None,
    ) -> Optional[int]:
        """Check the liquidity of a token against another token in the pool.

        Args:
            token_in: The input token address or contract.
            token_out: The output token address or contract.
            scale: The scale factor.
            block: The block number to query.

        Returns:
            The total output amount, or None if it cannot be determined.

        Examples:
            >>> balancer = BalancerV1(asynchronous=True)
            >>> await balancer.check_liquidity_against("0xabcdefabcdefabcdefabcdefabcdefabcdef", "0x1234567890abcdef1234567890abcdef12345678")
            1000
        """
        amount_in = await ERC20._get_scale_for(token_in) * scale
        with suppress(ValueError, VirtualMachineError, ContractLogicError):
            # across various dep versions we get these various excs
            view_split_exact_in = await self.exchange_proxy.viewSplitExactIn.coroutine(
                token_in,
                token_out,
                amount_in,
                32,  # NOTE: 32 is max
                block_identifier=block,
            )
            return view_split_exact_in["totalOutput"]

    @stuck_coro_debugger
    async def get_some_output(
        self, token_in: AddressOrContract, scale: int = 1, block: Optional[Block] = None
    ) -> Optional[Tuple[EthAddress, int]]:
        """Get some output for a given input token.

        Args:
            token_in: The input token address or contract.
            scale: The scale factor.
            block: The block number to query.

        Returns:
            A tuple containing the output token address and the total output amount, or None if it cannot be determined.

        Examples:
            >>> balancer = BalancerV1(asynchronous=True)
            >>> await balancer.get_some_output("0xabcdefabcdefabcdefabcdefabcdefabcdef")
            ('0x1234567890abcdef1234567890abcdef12345678', 1000)
        """
        for token_out in TOKENOUTS_TO_TRY:
            if output := await self.check_liquidity_against(
                token_in, token_out, block=block, scale=scale, sync=False
            ):
                return token_out, output

    @stuck_coro_debugger
    async def check_liquidity(
        self, token: Address, block: Block, ignore_pools: Tuple[Pool, ...] = ()
    ) -> int:
        """Check the liquidity of a token in the pool.

        Args:
            token: The token address.
            block: The block number to query.
            ignore_pools: A tuple of pools to ignore.

        Returns:
            The liquidity of the token in the pool.

        Examples:
            >>> balancer = BalancerV1(asynchronous=True)
            >>> await balancer.check_liquidity("0xabcdefabcdefabcdefabcdefabcdefabcdef", 12345678)
            1000
        """
        pools = [pool for pool in pools if pool not in ignore_pools]
        return (
            await BalancerV1Pool.check_liquidity.max(
                pools, token=token, block=block, sync=False
            )
            if pools
            else 0
        )
