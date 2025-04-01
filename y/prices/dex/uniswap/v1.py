from contextlib import suppress
from logging import DEBUG, getLogger
from typing import Any, Optional, Tuple

import a_sync
from a_sync import cgather
from brownie import ZERO_ADDRESS, chain

from y import ENVIRONMENT_VARIABLES as ENVS
from y._decorators import stuck_coro_debugger
from y.classes.common import ERC20
from y.constants import usdc
from y.contracts import Contract, contract_creation_block_async
from y.datatypes import Address, Block, Pool, UsdPrice
from y.exceptions import (
    ContractNotVerified,
    UnsupportedNetwork,
    continue_if_call_reverted,
)
from y.networks import Network
from y.utils.raw_calls import _decimals

logger = getLogger(__name__)


class UniswapV1(a_sync.ASyncGenericBase):
    factory = "0xc0a47dFe034B400B47bDaD5FecDa2621de6c4d95"

    def __init__(self, *, asynchronous: bool = False) -> None:
        """
        Initialize the UniswapV1 class.

        Args:
            asynchronous: If True, the class will operate in asynchronous mode.

        Raises:
            UnsupportedNetwork: If the current network is not Ethereum Mainnet.

        Examples:
            >>> uniswap_v1 = UniswapV1()
            >>> uniswap_v1.factory
            '0xc0a47dFe034B400B47bDaD5FecDa2621de6c4d95'
        """
        if chain.id != Network.Mainnet:
            raise UnsupportedNetwork(f"UniswapV1 does not suppport chainid {chain.id}")
        super().__init__()
        self.asynchronous = asynchronous

    @stuck_coro_debugger
    @a_sync.a_sync(ram_cache_maxsize=None)
    async def get_exchange(self, token_address: Address) -> Optional[Contract]:
        """
        Get the exchange contract for a given token address.

        Args:
            token_address: The address of the token for which to find the exchange.

        Returns:
            The exchange contract if it exists, otherwise None.

        Examples:
            >>> uniswap_v1 = UniswapV1()
            >>> exchange = await uniswap_v1.get_exchange("0xTokenAddress")
            >>> print(exchange)
            <Contract '0xExchangeAddress'>

        See Also:
            - :class:`~y.contracts.Contract`
        """
        factory = await Contract.coroutine(self.factory)
        exchange = await factory.getExchange.coroutine(token_address)
        if exchange != ZERO_ADDRESS:
            with suppress(ContractNotVerified):
                return await Contract.coroutine(exchange)

    @stuck_coro_debugger
    async def get_price(
        self,
        token_address: Address,
        block: Optional[Block],
        ignore_pools: Tuple[Pool, ...] = (),  # unused
        skip_cache: bool = ENVS.SKIP_CACHE,  # unused
    ) -> Optional[UsdPrice]:
        """
        Get the price of a token in USD.

        Args:
            token_address: The address of the token to get the price for.
            block: The block number at which to get the price.
            ignore_pools: Unused parameter.
            skip_cache: Unused parameter.

        Returns:
            The price of the token in USD, or None if the price cannot be determined.

        Examples:
            >>> uniswap_v1 = UniswapV1()
            >>> price = await uniswap_v1.get_price("0xTokenAddress", 12345678)
            >>> print(price)
            1.23

        See Also:
            - :class:`~y.datatypes.UsdPrice`
        """
        exchange, usdc_exchange, decimals = await cgather(
            self.get_exchange(token_address, sync=False),
            self.get_exchange(usdc, sync=False),
            _decimals(token_address, block, sync=False),
        )
        if exchange is None:
            return None

        try:
            eth_bought = await exchange.getTokenToEthInputPrice.coroutine(
                10**decimals, block_identifier=block
            )
            usdc_bought = (
                await usdc_exchange.getEthToTokenInputPrice.coroutine(
                    eth_bought, block_identifier=block
                )
                / 1e6
            )
            fees = 0.997**2
            return UsdPrice(usdc_bought / fees)
        except ValueError as e:
            if "invalid jump destination" in str(e):
                return None
            continue_if_call_reverted(e)

    @stuck_coro_debugger
    @a_sync.a_sync(ram_cache_maxsize=100_000, ram_cache_ttl=60 * 60)
    async def check_liquidity(
        self, token_address: Address, block: Block, ignore_pools: Tuple[Pool, ...] = ()
    ) -> int:
        """
        Check the liquidity of a token in its exchange.

        Args:
            token_address: The address of the token to check liquidity for.
            block: The block number at which to check liquidity.
            ignore_pools: A tuple of pools to ignore when checking liquidity.

        Returns:
            The liquidity of the token in its exchange.

        Examples:
            >>> uniswap_v1 = UniswapV1()
            >>> liquidity = await uniswap_v1.check_liquidity("0xTokenAddress", 12345678)
            >>> print(liquidity)
            1000000

        See Also:
            - :class:`~y.classes.common.ERC20`
        """
        if debug_logs_enabled := logger.isEnabledFor(DEBUG):
            log_debug(
                "checking Uniswap v1 liquidity for %s %s at %s ignoring %s",
                await ERC20(token_address, asynchronous=True).symbol,
                token_address,
                block,
                ignore_pools,
            )
        exchange = await self.get_exchange(token_address, sync=False)
        if exchange is None or exchange in ignore_pools:
            if debug_logs_enabled:
                log_debug("no Uniswap v1 exchange found for %s", token_address)
            return 0
        if block < await contract_creation_block_async(exchange):
            if debug_logs_enabled:
                log_debug("block %s prior to %s deploy block", block, exchange)
            return 0
        liquidity = await ERC20(token_address, asynchronous=True).balance_of(
            exchange, block
        )
        if debug_logs_enabled:
            log_debug(
                "Uniswap v1 liquidity for %s %s at %s is %s",
                await ERC20(token_address, asynchronous=True).symbol,
                token_address,
                block,
                liquidity,
            )
        return liquidity


def log_debug(msg: str, *args: Any) -> None:
    __logger_log(DEBUG, msg, args)


__logger_log = logger._log
