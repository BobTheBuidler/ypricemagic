from typing import Optional, Tuple

import a_sync
from a_sync import cgather
from brownie.exceptions import ContractNotFound

from y import ENVIRONMENT_VARIABLES as ENVS
from y import Contract
from y._decorators import stuck_coro_debugger
from y.classes.common import ERC20, WeiBalance
from y.datatypes import AnyAddressType, Block, UsdPrice, UsdValue
from y.exceptions import MessedUpBrownieContract
from y.utils import gather_methods, hasall

_CHECK_METHODS = "getReserves", "token0", "token1"
_TOKEN_METHODS = "token0()(address)", "token1()(address)"


async def is_generic_amm(lp_token_address: AnyAddressType) -> bool:
    """
    Check if the given address is a generic AMM LP token.

    Args:
        lp_token_address: The address to check.

    Returns:
        True if the address is a generic AMM LP token, False otherwise.

    Example:
        >>> address = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
        >>> is_amm = await is_generic_amm(address)
        >>> print(is_amm)
        False
    """
    try:
        contract = await Contract.coroutine(lp_token_address, require_success=False)
        return contract.verified and hasall(contract, _CHECK_METHODS)
    except ContractNotFound:
        return False
    except MessedUpBrownieContract:
        # probably false, can get more specific when there's a need.
        return False


class GenericAmm(a_sync.ASyncGenericBase):
    """
    A class for handling generic Automated Market Maker (AMM) Liquidity Pool (LP) tokens.

    This class provides methods to interact with and price generic AMM LP token contracts.
    """

    def __init__(self, *, asynchronous: bool = False) -> None:
        """
        Initialize the GenericAmm instance.

        Args:
            asynchronous (optional): Whether methods will return coroutines by default. Defaults to False.
        """
        super().__init__()
        self.asynchronous = asynchronous

    @stuck_coro_debugger
    async def get_price(
        self,
        lp_token_address: AnyAddressType,
        block: Optional[Block] = None,
        skip_cache: bool = ENVS.SKIP_CACHE,
    ) -> UsdPrice:
        """
        Get the price of the LP token in USD.

        Args:
            lp_token_address: The address of the LP token.
            block (optional): The block number to query. Defaults to None (latest).
            skip_cache (optional): Whether to skip cache. Defaults to :obj:`ENVS.SKIP_CACHE`.

        Returns:
            The price of the LP token in USD.

        Example:
            >>> amm = GenericAmm(asynchronous=True)
            >>> address = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
            >>> price = await amm.get_price(address)
            >>> print(price)
            0.5

        See Also:
            - :meth:`get_tvl`
            - :meth:`ERC20.total_supply_readable`
        """
        tvl, total_supply = await cgather(
            self.get_tvl(
                lp_token_address, block=block, skip_cache=skip_cache, sync=False
            ),
            ERC20(lp_token_address, asynchronous=True).total_supply_readable(
                block=block
            ),
        )
        if total_supply is None:
            return None
        elif total_supply == 0:
            return 0
        return UsdPrice(tvl / total_supply)

    @stuck_coro_debugger
    @a_sync.a_sync(cache_type="memory")
    async def get_tokens(self, lp_token_address: AnyAddressType) -> Tuple[ERC20, ERC20]:
        """
        Get the tokens in the AMM pool.

        Args:
            lp_token_address: The address of the LP token.

        Returns:
            A tuple containing the two ERC20 tokens in the pool.

        Example:
            >>> amm = GenericAmm(asynchronous=True)
            >>> address = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
            >>> tokens = await amm.get_tokens(address)
            >>> print(tokens)
            (ERC20(0x123...), ERC20(0x456...))

        See Also:
            - :class:`ERC20`
        """
        tokens = await gather_methods(lp_token_address, _TOKEN_METHODS)
        return tuple(ERC20(token, asynchronous=self.asynchronous) for token in tokens)

    @stuck_coro_debugger
    async def get_tvl(
        self,
        lp_token_address: AnyAddressType,
        block: Optional[Block] = None,
        skip_cache: bool = ENVS.SKIP_CACHE,
    ) -> UsdValue:
        """
        Get the Total Value Locked (TVL) in the AMM pool.

        Args:
            lp_token_address: The address of the LP token.
            block (optional): The block number to query. Defaults to None (latest).
            skip_cache (optional): Whether to skip cache. Defaults to :obj:`ENVS.SKIP_CACHE`.

        Returns:
            The Total Value Locked in USD.

        Example:
            >>> amm = GenericAmm(asynchronous=True)
            >>> address = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
            >>> tvl = await amm.get_tvl(address)
            >>> print(tvl)
            1000000.0

        See Also:
            - :meth:`get_price`
        """
        lp_token_contract = await Contract.coroutine(lp_token_address)
        tokens, reserves = await cgather(
            self.get_tokens(lp_token_address, sync=False),
            lp_token_contract.getReserves.coroutine(block_identifier=block),
        )
        reserves = (
            WeiBalance(reserve, token, block=block, skip_cache=skip_cache)
            for token, reserve in zip(tokens, reserves)
        )
        return UsdValue(await WeiBalance.value_usd.sum(reserves, sync=False))


generic_amm = GenericAmm(asynchronous=True)
"""A global instance of :class:`~GenericAmm` with asynchronous mode enabled."""
