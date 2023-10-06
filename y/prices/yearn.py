import asyncio
import logging
from decimal import Decimal
from typing import Optional

import a_sync
from brownie import chain

from y import Network
from y.classes.common import ERC20
from y.contracts import Contract, has_method, has_methods, probe
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.exceptions import (CantFetchParam, ContractNotVerified,
                          MessedUpBrownieContract)
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)

# NOTE: Yearn and Yearn-inspired

underlying_methods = [
    'token()(address)',
    'underlying()(address)',
    'native()(address)',
    'want()(address)',
    'input()(address)',
    'asset()(address)',
    'wmatic()(address)',
    'wbnb()(address)',
    'based()(address)',
]

share_price_methods = [
    'pricePerShare()(uint)',
    'getPricePerShare()(uint)',
    'getPricePerFullShare()(uint)',
    'getSharesToUnderlying()(uint)',
    'exchangeRate()(uint)',
]

force_false = {
    Network.Mainnet: [
        "0x8751D4196027d4e6DA63716fA7786B5174F04C15",  # wibBTC
        "0xF0a93d4994B3d98Fb5e3A2F90dBc2d69073Cb86b",  # PWRD
    ],
}.get(chain.id, [])

@a_sync.a_sync(default='sync', cache_type='memory')
async def is_yearn_vault(token: AnyAddressType) -> bool:
    # wibbtc returns True here even though it doesn't meet the criteria.
    # TODO figure out a better fix. For now I need a fix asap so this works.
    if chain.id == Network.Mainnet and str(token) == "0x8751D4196027d4e6DA63716fA7786B5174F04C15":
        return False
    
    # Yearn-like contracts can use these formats
    result = any(
        await asyncio.gather(
            has_methods(token, ('pricePerShare()(uint)','getPricePerShare()(uint)','getPricePerFullShare()(uint)','getSharesToUnderlying()(uint)'), any, sync=False),
            has_methods(token, ('exchangeRate()(uint)','underlying()(address)'), sync=False),
        )
    )

    # pricePerShare can revert if totalSupply == 0, which would cause `has_methods` to return `False`,
    # but it might still be a vault. This section will correct `result` for problematic vaults.
    if result is False:
        try: 
            contract = await Contract.coroutine(token)
            result = any([
                hasattr(contract,'pricePerShare'),
                hasattr(contract,'getPricePerShare'),
                hasattr(contract,'getPricePerFullShare'),
                hasattr(contract,'getSharesToUnderlying'),
            ])
        except (ContractNotVerified, MessedUpBrownieContract): pass

    return result

@a_sync.a_sync(default='sync')
async def get_price(token: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
    return await YearnInspiredVault(token).price(block=block, sync=False)

class YearnInspiredVault(ERC20):
    # v1 vaults use getPricePerFullShare scaled to 18 decimals
    # v2 vaults use pricePerShare scaled to underlying token decimals
    # yearnish clones use all sorts of other things, we gotchu covered
    
    @a_sync.aka.cached_property
    async def underlying(self) -> ERC20:
        # special cases
        if chain.id == Network.Arbitrum and self.address == '0x57c7E0D43C05bCe429ce030132Ca40F6FA5839d7':
            return ERC20(await raw_call(self.address, 'usdl()', output='address', sync=False), asynchronous=self.asynchronous)

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
            underlying = await raw_call(self.address, method, output='address', sync=False)
        
        if not underlying:
            # certain reaper vaults
            lend_platform = await self.has_method('lendPlatform()(address)', return_response=True, sync=False)
            if lend_platform:
                underlying = await has_method(lend_platform, 'underlying()(address)', return_response=True, sync=False)

        if underlying: return ERC20(underlying)
        else: raise CantFetchParam(f'underlying for {self.__repr__()}')

    a_sync.a_sync(cache_type='memory', ram_cache_maxsize=1000)
    async def share_price(self, block: Optional[Block] = None) -> Optional[Decimal]:
        method, share_price = await probe(self.address, share_price_methods, block=block, return_method=True)

        if share_price is None:
            # this is for element vaults, probe fails because method requires input
            try:
                contract = self.contract
                if hasattr(contract, 'getSharesToUnderlying'):
                    share_price = contract.getSharesToUnderlying.coroutine(await self.scale, block_identifier=block)
            except ContractNotVerified:
                pass

        if share_price is not None:
            if method == 'getPricePerFullShare()(uint)':
                # v1 vaults use getPricePerFullShare scaled to 18 decimals
                return share_price / Decimal(10 ** 18)
            underlying = await self.__underlying__(sync=False)
            return Decimal(share_price / await underlying.__scale__(sync=False))
            
        elif await raw_call(self.address, 'totalSupply()', output='int', block=block, return_None_on_failure=True, sync=False) == 0:
            return None
        
        else:
            raise CantFetchParam(f'share_price for {self.__repr__()}')
    
    a_sync.a_sync(cache_type='memory', ram_cache_maxsize=1000)
    async def price(self, block: Optional[Block] = None) -> UsdPrice:
        share_price, underlying = await asyncio.gather(self.share_price(block=block, sync=False), self.__underlying__(sync=False))
        if share_price is None:
            return None
        return UsdPrice(share_price * Decimal(await underlying.price(block=block, sync=False)))
