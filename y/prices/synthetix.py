import asyncio
import logging
from typing import List, Optional

import a_sync
from brownie import chain
from brownie.convert.datatypes import EthAddress, HexString
from eth_abi import encode_single
from multicall import Call

from y import convert
from y import ENVIRONMENT_VARIABLES as ENVS
from y.contracts import Contract, has_method
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.exceptions import UnsupportedNetwork, call_reverted
from y.networks import Network

logger = logging.getLogger(__name__)

addresses = {
    Network.Mainnet: '0x823bE81bbF96BEc0e25CA13170F5AaCb5B79ba83',
    Network.Optimism: '0x95A6a3f44a70172E7d50a9e28c85Dfd712756B8C',
}


class Synthetix(a_sync.ASyncGenericSingleton):
    def __init__(self, asynchronous: bool = False) -> None:
        if chain.id not in addresses:
            raise UnsupportedNetwork("synthetix is not supported on this network")
        self.asynchronous = asynchronous
        super().__init__()
    
    @a_sync.aka.property
    async def address_resolver(self) -> Contract:
        return await Contract.coroutine(addresses[chain.id])

    @a_sync.a_sync(ram_cache_maxsize=256)
    async def get_address(self, name: str, block: Block = None) -> Contract:
        """
        Get contract from Synthetix registry.
        See also https://docs.synthetix.io/addresses/
        """
        address_resolver = await self.__address_resolver__(sync=False)
        address = await address_resolver.getAddress.coroutine(encode_single('bytes32', name.encode()), block_identifier=block)
        proxy = await Contract.coroutine(address)
        return await Contract.coroutine(await proxy.target.coroutine(block_identifier=block)) if hasattr(proxy, 'target') else proxy

    @a_sync.aka.cached_property
    async def synths(self) -> List[EthAddress]:
        """
        Get target addresses of all synths.
        """
        proxy_erc20 = await self.get_address('ProxyERC20', sync=False)
        synth_count = await proxy_erc20.availableSynthCount.coroutine()
        synths = await asyncio.gather(*[proxy_erc20.availableSynths.coroutine(i) for i in range(synth_count)])
        logger.info('loaded %s synths', len(synths))
        return synths
        
    async def is_synth(self, token: AnyAddressType) -> bool:
        """
        Check if a token is a synth.
        """
        token = convert.to_address(token)
        if await synthetix.get_currency_key(token, sync=False):
            return True
        if await has_method(token, 'target()(address)', sync=False):
            target = await Call(token, 'target()(address)').coroutine()
            return target in await synthetix.synths and await Call(target, 'proxy()(address)').coroutine() == token
        return False
    
    @a_sync.a_sync(cache_type='memory', ram_cache_ttl=ENVS.CACHE_TTL)
    async def get_currency_key(self, token: AnyAddressType) -> Optional[HexString]:
        target = await Call(token, ['target()(address)']).coroutine() if await has_method(token, 'target()(address)', sync=False) else token
        return await Call(target, ['currencyKey()(bytes32)']).coroutine() if await has_method(token, 'currencyKey()(bytes32)', sync=False) else None
    
    async def get_price(self, token: AnyAddressType, block: Optional[Block] = None) -> Optional[UsdPrice]:
        """
        Get a price of a synth in dollars.
        """
        token = convert.to_address(token)
        try:
            rates, key = await asyncio.gather(
                self.get_address('ExchangeRates', block=block, sync=False),
                self.get_currency_key(token, sync=False)
            )
            return UsdPrice(await rates.rateForCurrency.coroutine(key, block_identifier=block) / 10 ** 18)
        except Exception as e:
            if call_reverted(e):
                return None
            raise

synthetix = Synthetix(asynchronous=True) if chain.id in addresses else set()
