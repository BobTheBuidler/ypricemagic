from decimal import Decimal
from logging import DEBUG, getLogger
from typing import Optional, Tuple

import a_sync
from a_sync import ASyncCachedPropertyDescriptor, cgather
from a_sync.a_sync import HiddenMethodDescriptor
from dank_mids.exceptions import Revert
from multicall.call import Call
from typing_extensions import Self
from web3.exceptions import ContractLogicError

from y import ENVIRONMENT_VARIABLES as ENVS
from y import Network
from y._decorators import stuck_coro_debugger
from y.classes.common import ERC20
from y.constants import CHAINID, CONNECTED_TO_MAINNET, weth
from y.contracts import Contract, has_method, has_methods, probe
from y.datatypes import AnyAddressType, Block, Pool, UsdPrice
from y.exceptions import (
    CantFetchParam,
    ContractNotVerified,
    MessedUpBrownieContract,
    PriceError,
    yPriceMagicError,
)
from y.utils.cache import optional_async_diskcache
from y.utils.logging import get_price_logger
from y.utils.raw_calls import raw_call

logger = getLogger(__name__)

# NOTE: Yearn and Yearn-inspired

underlying_methods = (
    "token()(address)",
    "underlying()(address)",
    "native()(address)",
    "want()(address)",
    "input()(address)",
    "asset()(address)",
    "wmatic()(address)",
    "wbnb()(address)",
    "based()(address)",
)
"""
List of methods which might be used to get the underlying asset of a vault.
"""

share_price_methods = (
    "pricePerShare()(uint)",
    "getPricePerShare()(uint)",
    "getPricePerFullShare()(uint)",
    "getSharesToUnderlying()(uint)",
    "exchangeRate()(uint)",
)
"""
List of methods which might be used to get the share price of a vault.
"""

# wibbtc returns True here even though it doesn't meet the criteria.
# TODO figure out a better fix. For now I need a fix asap so this works.
# NOTE turns out I never fixed it and there are more now. Womp.
force_false = {
    Network.Mainnet: (
        "0x8751D4196027d4e6DA63716fA7786B5174F04C15",  # wibBTC
        "0xF0a93d4994B3d98Fb5e3A2F90dBc2d69073Cb86b",  # PWRD
        "0x35Ec69A77B79c255e5d47D5A3BdbEFEfE342630c",  # ynLSDe
    ),
}


@a_sync.a_sync(default="sync", cache_type="memory", ram_cache_ttl=30 * 60)
@stuck_coro_debugger
@optional_async_diskcache
async def is_yearn_vault(token: AnyAddressType) -> bool:
    if str(token) in force_false.get(CHAINID, ()):
        return False

    # Yearn-like contracts can use these formats
    result = any(
        await cgather(
            has_methods(
                token,
                (
                    "pricePerShare()(uint)",
                    "getPricePerShare()(uint)",
                    "getPricePerFullShare()(uint)",
                    "getSharesToUnderlying()(uint)",
                ),
                any,
                sync=False,
            ),
            has_methods(token, ("exchangeRate()(uint)", "underlying()(address)"), sync=False),
        )
    )

    # pricePerShare can revert if totalSupply == 0, which would cause `has_methods` to return `False`,
    # but it might still be a vault. This section will correct `result` for problematic vaults.
    if not result:
        try:
            contract = await Contract.coroutine(token)
        except (ContractNotVerified, MessedUpBrownieContract):
            pass
        else:
            result = (
                hasattr(contract, "pricePerShare")
                or hasattr(contract, "getPricePerShare")
                or hasattr(contract, "getPricePerFullShare")
                or hasattr(contract, "getSharesToUnderlying")
                or hasattr(contract, "convertToAssets")
            )
    return result


@a_sync.a_sync(default="sync")
async def get_price(
    token: AnyAddressType,
    block: Optional[Block] = None,
    skip_cache: bool = ENVS.SKIP_CACHE,
    ignore_pools: Tuple[Pool, ...] = (),
) -> UsdPrice:
    return await YearnInspiredVault(token).price(
        block=block, skip_cache=skip_cache, ignore_pools=ignore_pools, sync=False
    )


_BEEFY_METHODS = {
    "BeefyVaultV6Matic": "wmatic()",
    "BeefyVenusVaultBNB": "wbnb()",
}


class YearnInspiredVault(ERC20):
    """
    Represents a vault token from Yearn or a similar protocol.

    This class extends ERC20 and provides methods to interact with vaults,
    including fetching the underlying asset, share price, and token price.
    """

    # defaults are stored as class vars to keep instance dicts smaller

    _get_share_price = None
    """
    Cached method to get the share price.
    
    This class will probe various share price methods to find the correct one, and then save it for reuse.
    """
    # v1 vaults use getPricePerFullShare scaled to 18 decimals
    # v2 vaults use pricePerShare scaled to underlying token decimals
    # yearnish clones use all sorts of other things, we gotchu covered

    # mypy helpers
    underlying: ASyncCachedPropertyDescriptor[Self, ERC20]
    __underlying__: HiddenMethodDescriptor[Self, ERC20]

    @a_sync.aka.cached_property
    async def underlying(self) -> ERC20:
        """
        Fetches the underlying asset of the vault.

        Returns:
            The underlying ERC20 token.

        Raises:
            CantFetchParam: If the underlying asset cannot be determined.

        Special Cases:
            1. Arbitrum USDL: For the specific address 0x57c7E0D43C05bCe429ce030132Ca40F6FA5839d7 on Arbitrum,
               it uses the 'usdl()' method to fetch the underlying token.
            2. Beefy Vaults: For certain Beefy vaults (BeefyVaultV6Matic and BeefyVenusVaultBNB),
               it uses 'wmatic()' or 'wbnb()' methods respectively.
            3. Reaper Vaults: For certain Reaper vaults, it checks for a 'lendPlatform()' method
               and then queries the 'underlying()' method on the lend platform contract.

        Example:
            >>> vault = YearnInspiredVault("0x5f18C75AbDAe578b483E5F43f12a39cF75b973a9")  # yvUSDC
            >>> underlying = vault.underlying()
            >>> underlying.address
            "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"  # USDC address
        """
        # special cases
        if CHAINID == Network.Arbitrum:
            if self.address == "0x57c7E0D43C05bCe429ce030132Ca40F6FA5839d7":
                underlying = await raw_call(self.address, "usdl()", output="address", sync=False)
                return ERC20(underlying, asynchronous=self.asynchronous)
        elif CONNECTED_TO_MAINNET and self.address == "0x09db87A538BD693E9d08544577d5cCfAA6373A48":
            # ynETH yield nest has no method for underlying
            return ERC20(weth, asynchronous=self.asynchronous)

        try:
            underlying = await probe(self.address, underlying_methods)
        except AssertionError:
            # special handler for some strange beefy vaults
            beefy_method = _BEEFY_METHODS.get(await self.__build_name__)
            if beefy_method is None:
                raise
            underlying = await raw_call(self.address, beefy_method, output="address", sync=False)

        if underlying is None:
            # certain reaper vaults
            try:
                lend_platform = await self.has_method(
                    "lendPlatform()(address)", return_response=True, sync=False
                )
            except ContractLogicError:
                pass
            else:
                if lend_platform:
                    underlying = await has_method(
                        lend_platform,
                        "underlying()(address)",
                        return_response=True,
                        sync=False,
                    )

        if underlying is not None:
            underlying = ERC20(underlying, asynchronous=self.asynchronous)
            if logger.isEnabledFor(DEBUG):
                logger._log(
                    DEBUG,
                    "%s %s underlying is %s %s",
                    (
                        await self.__symbol__,
                        self,
                        await underlying.__symbol__,
                        underlying,
                    ),
                )
            return underlying
        raise CantFetchParam(f"underlying for {self}")

    @a_sync.a_sync(cache_type="memory", ram_cache_maxsize=1000)
    async def share_price(self, block: Optional[Block] = None) -> Optional[Decimal]:
        """
        Calculates the share price of the vault.

        Args:
            block (optional): The block number to query. Defaults to the latest block.

        Returns:
            The share price of the vault, or None if the vault's total supply is zero.

        Raises:
            CantFetchParam: If the share price cannot be fetched or calculated.

        Example:
            >>> vault = YearnInspiredVault("0x5f18C75AbDAe578b483E5F43f12a39cF75b973a9")  # yvUSDC
            >>> share_price = await vault.share_price(block=14_000_000)
            >>> print(f"{share_price:.6f}")
            1.096431
        """
        if self._get_share_price:
            try:
                share_price = await self._get_share_price.coroutine(block_id=block)
            except Exception as e:
                logger.debug("exc %s when fetching share price for %s", e, self)
                share_price = await probe(self.address, share_price_methods, block=block)
        else:
            share_price_method, share_price = await probe(
                self.address, share_price_methods, block=block, return_method=True
            )
            if share_price_method:
                self._get_share_price = Call(self.address, [share_price_method])

        if share_price is None:
            # this is for element vaults and other 'scaled' share price functions. probe fails because method requires input
            try:
                contract = await Contract.coroutine(self.address)
            except ContractNotVerified:
                pass
            else:
                for method in ("convertToAssets", "getSharesToUnderlying"):
                    if contract_call := getattr(contract, method, None):

                        scale = await self.__scale__

                        class call:
                            # a hacky way we can cache this weird case and save calls
                            function = method

                            @staticmethod
                            async def coroutine(block_id: Optional[Block]) -> int:
                                return await contract_call.coroutine(
                                    scale, block_identifier=block_id
                                )

                        try:
                            share_price = await call.coroutine(block_id=block)
                        except (ContractLogicError, Revert):
                            pass
                        else:
                            self._get_share_price = call

        if share_price is not None:
            if (
                self._get_share_price
                and self._get_share_price.function == "getPricePerFullShare()(uint)"
            ):
                # v1 vaults use getPricePerFullShare scaled to 18 decimals
                return share_price / Decimal(10**18)
            underlying = await self.__underlying__
            return Decimal(share_price) / await underlying.__scale__

        elif (
            await raw_call(
                self.address,
                "totalSupply()",
                output="int",
                block=block,
                return_None_on_failure=True,
                sync=False,
            )
            == 0
        ):
            return None

        else:
            raise CantFetchParam(f"share_price for {self}")

    a_sync.a_sync(cache_type="memory", ram_cache_maxsize=1000)

    async def price(
        self,
        block: Optional[Block] = None,
        ignore_pools: Tuple[Pool, ...] = (),
        skip_cache: bool = ENVS.SKIP_CACHE,
    ) -> UsdPrice:
        """
        Calculates the USD price of the vault token.

        Args:
            block (optional): The block number to query. Defaults to the latest block.
            ignore_pools: Pools to ignore when calculating the price.
            skip_cache: Whether to skip the cache when fetching prices.

        Returns:
            The USD price of the vault token.

        Example:
            >>> vault = YearnInspiredVault("0x5f18C75AbDAe578b483E5F43f12a39cF75b973a9")  # yvUSDC
            >>> price = vault.price(block=14_000_000)
            >>> print(f"{price:.6f}")
            1.096431  # The price of yvUSDC in USD
        """
        logger = get_price_logger(self.address, block=None, extra="yearn")
        underlying: ERC20
        try:
            share_price, underlying = await cgather(
                self.share_price(block=block, sync=False), self.__underlying__
            )
        except CantFetchParam:
            return None
        if share_price is None:
            return None
        logger.debug("%s share price at block %s: %s", self, block, share_price)
        try:
            price = UsdPrice(
                share_price
                * Decimal(
                    await underlying.price(
                        block=block,
                        ignore_pools=ignore_pools,
                        skip_cache=skip_cache,
                        sync=False,
                    )
                )
            )
        except yPriceMagicError as e:
            if not isinstance(e.exception, PriceError):
                raise
            price = None
        logger.debug("%s price at block %s: %s", self, block, price)
        return price
