import logging
from functools import cached_property, lru_cache
from typing import Any, Optional

from brownie import chain
from y import Network
from y.classes.common import ERC20, WeiBalance
from y.contracts import Contract, has_method, has_methods, probe
from y.datatypes import UsdPrice
from y.decorators import log
from y.exceptions import (CantFetchParam, ContractNotVerified,
                          MessedUpBrownieContract)
from y.typing import AnyAddressType, Block
from y.utils.cache import memory
from y.utils.raw_calls import raw_call

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

@log(logger)
@memory.cache()
def is_yearn_vault(token: AnyAddressType) -> bool:
    # Yearn-like contracts can use these formats
    result = any([
        has_methods(token, ['pricePerShare()(uint)','getPricePerShare()(uint)','getPricePerFullShare()(uint)','getSharesToUnderlying()(uint)'], any),
        has_methods(token, ['exchangeRate()(uint)','underlying()(address)']),
    ])

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

@log(logger)
def get_price(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    return YearnInspiredVault(token).price(block=block)

class YearnInspiredVault(ERC20):
    # v1 vaults use getPricePerFullShare scaled to 18 decimals
    # v2 vaults use pricePerShare scaled to underlying token decimals
    # yearnish clones use all sorts of other things, we gotchu covered
    def __init__(self, address: AnyAddressType, *args: Any, **kwargs: Any) -> None:
        super().__init__(address, *args, **kwargs)
    
    def __repr__(self) -> str:
        if self.symbol:
            return f"<YearnInspiredVault {self.symbol} '{self.address}'>"
    
    @cached_property
    @log(logger)
    def underlying(self) -> ERC20:
        # special cases
        if chain.id == Network.Arbitrum and self.address == '0x57c7E0D43C05bCe429ce030132Ca40F6FA5839d7':
            return ERC20(raw_call(self.address, 'usdl()', output='address'))


        try:
            underlying = probe(self.address, underlying_methods)
        except AssertionError:
            # special handler for some strange beefy vaults
            method = {
                "BeefyVaultV6Matic": "wmatic()",
                "BeefyVenusVaultBNB": "wbnb()",
            }.get(self.build_name, None)

            if not method: raise
            underlying = raw_call(self.address, method, output='address')
        
        if not underlying:
            # certain reaper vaults
            lend_platform = self.has_method('lendPlatform()(address)', return_response=True)
            if lend_platform:
                underlying = has_method(lend_platform, 'underlying()(address)', return_response=True)

        if underlying: return ERC20(underlying)
        else: raise CantFetchParam(f'underlying for {self.__repr__()}')

    @log(logger)
    @lru_cache
    def share_price(self, block: Optional[Block] = None) -> WeiBalance:
        share_price = probe(self.address, share_price_methods, block=block)

        if share_price is None:
            # this is for element vaults, probe fails because method requires input
            try:
                contract = self.contract
                if hasattr(contract, 'getSharesToUnderlying'):
                    share_price = contract.getSharesToUnderlying(self.scale,block_identifier=block)
            except ContractNotVerified:
                pass

        if share_price is not None:
            return WeiBalance(share_price, self.underlying, block=block)
        elif raw_call(self.address, 'totalSupply()', output='int', block=block, return_None_on_failure=True) == 0:
            return WeiBalance(0, self.underlying, block=block)
        else:
            raise CantFetchParam(f'share_price for {self.__repr__()}')
    
    @log(logger)
    @lru_cache
    def price(self, block: Optional[Block] = None) -> UsdPrice:
        return UsdPrice(self.share_price(block=block).readable * self.underlying.price(block=block))
