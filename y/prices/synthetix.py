import asyncio
import logging
from functools import cached_property
from typing import List, Optional

from async_lru import alru_cache
from async_property import async_cached_property
from brownie import chain
from brownie.convert.datatypes import EthAddress, HexString
from eth_abi import encode_single
from multicall import Call
from multicall.utils import await_awaitable

from y import convert
from y.classes.singleton import Singleton
from y.contracts import Contract, has_method_async
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.exceptions import UnsupportedNetwork, call_reverted
from y.networks import Network

logger = logging.getLogger(__name__)

addresses = {
    Network.Mainnet: '0x823bE81bbF96BEc0e25CA13170F5AaCb5B79ba83',
}


class Synthetix(metaclass=Singleton):
    def __init__(self) -> None:
        if chain.id not in addresses:
            raise UnsupportedNetwork("synthetix is not supported on this network")
    
    @async_cached_property
    async def address_resolver(self) -> Contract:
        return await Contract.coroutine(addresses[chain.id])

    @alru_cache(maxsize=256)
    async def get_address(self, name: str, block: Block = None) -> Contract:
        """
        Get contract from Synthetix registry.
        See also https://docs.synthetix.io/addresses/
        """
        address_resolver = await self.address_resolver
        address = await address_resolver.getAddress.coroutine(encode_single('bytes32', name.encode()), block_identifier=block)
        proxy = await Contract.coroutine(address)
        return await Contract.coroutine(proxy.target()) if hasattr(proxy, 'target') else proxy

    @cached_property
    async def synths(self) -> List[EthAddress]:
        """
        Get target addresses of all synths.
        """
        proxy_erc20 = await self.get_address('ProxyERC20')
        synth_count = await proxy_erc20.availableSynthCount.coroutine()
        synths = await asyncio.gather(*[proxy_erc20.availableSynths(i) for i in range(synth_count)])
        logger.info(f'loaded {len(synths)} synths')
        return synths
    '''
    def __contains__(self, token: AnyAddressType) -> bool:
        """
        Check if a token is a synth.
        """
        token = convert.to_address(token)
        if synthetix.get_currency_key(token):
            return True
        if has_method(token, 'target()(address)'):
            target = Call(token, 'target()(address)')()
            return target in synthetix.synths and Call(target, 'proxy()(address)')() == token
        return False
    '''
    async def is_synth(self, token: AnyAddressType) -> bool:
        """
        Check if a token is a synth.
        """
        token = convert.to_address(token)
        if await synthetix.get_currency_key_async(token):
            return True
        if await has_method_async(token, 'target()(address)'):
            target = await Call(token, 'target()(address)').coroutine()
            return target in await synthetix.synths and await Call(target, 'proxy()(address)').coroutine() == token
        return False

    def get_currency_key(self, token: AnyAddressType) -> Optional[HexString]:
        return await_awaitable(self.get_currency_key_async(token))
    
    @alru_cache(maxsize=None)
    async def get_currency_key_async(self, token: AnyAddressType) -> Optional[HexString]:
        target = await Call(token, ['target()(address)']).coroutine() if await has_method_async(token,'target()(address)') else token
        return await Call(target, ['currencyKey()(bytes32)']).coroutine() if await has_method_async(token,'currencyKey()(bytes32)') else None

    def get_price(self, token: AnyAddressType, block: Optional[Block] = None) -> Optional[UsdPrice]:
        return await_awaitable(self.get_price_async(token, block=block))
    
    async def get_price_async(self, token: AnyAddressType, block: Optional[Block] = None) -> Optional[UsdPrice]:
        """
        Get a price of a synth in dollars.
        """
        token = convert.to_address(token)
        try:
            rates, key = await asyncio.gather(self.get_address('ExchangeRates', block=block), self.get_currency_key_async(token))
            return UsdPrice(await rates.rateForCurrency.coroutine(key, block_identifier=block) / 10 ** 18)
        except Exception as e:
            if call_reverted(e):
                return None
            raise


try:
    synthetix = Synthetix()
except UnsupportedNetwork:
    synthetix = set()
