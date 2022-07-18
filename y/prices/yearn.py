import logging
from functools import cached_property
from typing import Any, Optional

from async_lru import alru_cache
from async_property import async_cached_property
from brownie import chain
from multicall.utils import await_awaitable, gather
from y import Network
from y.classes.common import ERC20
from y.contracts import Contract, has_method_async, has_methods_async, probe
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.exceptions import (CantFetchParam, ContractNotVerified,
                          MessedUpBrownieContract)
from y.utils.cache import memory
from y.utils.logging import yLazyLogger
from y.utils.raw_calls import raw_call_async

logger = logging.getLogger(__name__)

# NOTE: Yearn and Yearn-inspired

underlying_methods = [
    'token()(address)',
    'underlying()(address)',
    'native()(address)',
    'want()(address)',
    'input()(address)'
    'wmatic()(address)',
    'wbnb()(address)',
    'based()(address)',
]

share_price_methods = [
    'pricePerShare()(uint)',
    'getPricePerShare()(uint)',
    'getPricePerFullShare()(uint)',
    'getSharesToUnderlying()(uint)',
    'exchangeRate()(uint)'
]

force_false = {
    Network.Mainnet: [
        "0x8751D4196027d4e6DA63716fA7786B5174F04C15",
    ],
}.get(chain.id, [])

@memory.cache()
@yLazyLogger(logger)
def is_yearn_vault(token: AnyAddressType) -> bool:
    return await_awaitable(is_yearn_vault_async(token))

@yLazyLogger(logger)
@alru_cache(maxsize=None)
async def is_yearn_vault_async(token: AnyAddressType) -> bool:
    
    # Yearn-like contracts can use these formats
    result = any(
        await gather([
            has_methods_async(token, ('pricePerShare()(uint)','getPricePerShare()(uint)','getPricePerFullShare()(uint)','getSharesToUnderlying()(uint)'), any),
            has_methods_async(token, ('exchangeRate()(uint)','underlying()(address)')),
        ])
    )

    # pricePerShare can revert if totalSupply == 0, which would cause `has_methods` to return `False`,
    # but it might still be a vault. This section will correct `result` for problematic vaults.
    if result is False:
        try: 
            contract = Contract(token)
            result = any([
                hasattr(contract,'pricePerShare'),
                hasattr(contract,'getPricePerShare'),
                hasattr(contract,'getPricePerFullShare'),
                hasattr(contract,'getSharesToUnderlying'),
            ])
        except (ContractNotVerified, MessedUpBrownieContract): pass

    return result

@yLazyLogger(logger)
def get_price(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    return YearnInspiredVault(token).price(block=block)

@yLazyLogger(logger)
async def get_price_async(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    return await YearnInspiredVault(token).price_async(block=block)

class YearnInspiredVault(ERC20):
    # v1 vaults use getPricePerFullShare scaled to 18 decimals
    # v2 vaults use pricePerShare scaled to underlying token decimals
    # yearnish clones use all sorts of other things, we gotchu covered
    def __init__(self, address: AnyAddressType, *args: Any, **kwargs: Any) -> None:
        super().__init__(address, *args, **kwargs)
    
    def __repr__(self) -> str:
        try:
            if self.symbol:
                return f"<YearnInspiredVault {self.symbol} '{self.address}'>"
        except RuntimeError:
            pass
        return f"<YearnInspiredVault '{self.address}'>"
    
    @cached_property
    @yLazyLogger(logger)
    def underlying(self) -> ERC20:
        return await_awaitable(self.underlying_async)
    
    @yLazyLogger(logger)
    @async_cached_property
    async def underlying_async(self) -> ERC20:
        # special cases
        if chain.id == Network.Arbitrum and self.address == '0x57c7E0D43C05bCe429ce030132Ca40F6FA5839d7':
            return ERC20(await raw_call_async(self.address, 'usdl()', output='address'))

        try:
            underlying = await probe(self.address, underlying_methods)
        except AssertionError:
            # special handler for some strange beefy vaults
            method = {
                "BeefyVaultV6Matic": "wmatic()",
                "BeefyVenusVaultBNB": "wbnb()",
            }.get(self.build_name, None)

            if not method:
                raise
            underlying = await raw_call_async(self.address, method, output='address')
        
        if not underlying:
            # certain reaper vaults
            lend_platform = await self.has_method_async('lendPlatform()(address)', return_response=True)
            if lend_platform:
                underlying = await has_method_async(lend_platform, 'underlying()(address)', return_response=True)

        if underlying: return ERC20(underlying)
        else: raise CantFetchParam(f'underlying for {self.__repr__()}')

    @yLazyLogger(logger)
    def share_price(self, block: Optional[Block] = None) -> Optional[float]:
        return await_awaitable(self.share_price_async(block=block))
    
    @yLazyLogger(logger)
    @alru_cache(maxsize=1000)
    async def share_price_async(self, block: Optional[Block] = None) -> Optional[float]:
        method, share_price = await probe(self.address, share_price_methods, block=block, return_method=True)

        if share_price is None:
            # this is for element vaults, probe fails because method requires input
            try:
                contract = self.contract
                if hasattr(contract, 'getSharesToUnderlying'):
                    share_price = contract.getSharesToUnderlying.coroutine(await self.scale,block_identifier=block)
            except ContractNotVerified:
                pass

        if share_price is not None:
            if method == 'getPricePerFullShare()(uint)':
                # v1 vaults use getPricePerFullShare scaled to 18 decimals
                return share_price / 1e18
            underlying = await self.underlying_async
            return share_price / await underlying.scale
            
        elif await raw_call_async(self.address, 'totalSupply()', output='int', block=block, return_None_on_failure=True) == 0:
            return None
        
        else:
            raise CantFetchParam(f'share_price for {self.__repr__()}')
    
    @yLazyLogger(logger)
    def price(self, block: Optional[Block] = None) -> UsdPrice:
        return await_awaitable(self.price_async(block=block))
    
    @yLazyLogger(logger)
    @alru_cache(maxsize=1000)
    async def price_async(self, block: Optional[Block] = None) -> UsdPrice:
        underlying = await self.underlying_async
        share_price, underlying_price = await gather([
            self.share_price_async(block=block),
            underlying.price_async(block=block)
        ])
        return UsdPrice(share_price * underlying_price)
