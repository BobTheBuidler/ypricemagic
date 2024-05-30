import asyncio
import logging
from typing import Callable, List, Optional

import a_sync
from a_sync.a_sync import HiddenMethodDescriptor
from brownie import chain
from brownie.convert.datatypes import EthAddress, HexString
from multicall import Call
from typing_extensions import Self

from y import convert
from y import ENVIRONMENT_VARIABLES as ENVS
from y.contracts import Contract, has_method
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.exceptions import UnsupportedNetwork, call_reverted
from y.networks import Network
from y.utils import a_sync_ttl_cache

try:
    from eth_abi import encode
    encode_bytes: Callable[[str], bytes] = lambda s: encode(["bytes32"], [s.encode()])
except ImportError:
    from eth_abi import encode_single
    encode_bytes: Callable[[str], bytes] = lambda s: encode_single("bytes32", s.encode())

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
    __address_resolver__: HiddenMethodDescriptor[Self, Contract]

    @a_sync.a_sync(ram_cache_maxsize=256)
    async def get_address(self, name: str, block: Block = None) -> Contract:
        """
        Get contract from Synthetix registry.
        See also https://docs.synthetix.io/addresses/
        """
        address_resolver = await self.__address_resolver__
        address = await address_resolver.getAddress.coroutine(encode_bytes(name), block_identifier=block)
        proxy = await Contract.coroutine(address)
        return await Contract.coroutine(await proxy.target.coroutine(block_identifier=block)) if hasattr(proxy, 'target') else proxy

    @a_sync.aka.cached_property
    async def synths(self) -> List[EthAddress]:
        """
        Get target addresses of all synths.
        """
        proxy_erc20 = await self.get_address('ProxyERC20', sync=False)
        synths = await proxy_erc20.availableSynths.map(range(await proxy_erc20.availableSynthCount))
        logger.info('loaded %s synths', len(synths))
        return synths
        
    async def is_synth(self, token: AnyAddressType) -> bool:
        """returns `True` if a `token` is a synth, `False` if not"""
        token = convert.to_address(token)
        try:
            if await synthetix.get_currency_key(token, sync=False):
                return True
            if await has_method(token, 'target()(address)', sync=False):
                target = await Call(token, 'target()(address)')
                return target in await synthetix.synths and await Call(target, 'proxy()(address)') == token
            return False
        except Exception as e:
            if "invalid jump destination" in str(e):
                return False
            raise
    
    @a_sync_ttl_cache
    async def get_currency_key(self, token: AnyAddressType) -> Optional[HexString]:
        target = await Call(token, ['target()(address)']) if await has_method(token, 'target()(address)', sync=False) else token
        return await Call(target, ['currencyKey()(bytes32)']) if await has_method(token, 'currencyKey()(bytes32)', sync=False) else None
    
    async def get_price(self, token: AnyAddressType, block: Optional[Block] = None) -> Optional[UsdPrice]:
        """
        Get a price of a synth in dollars.
        """
        token = convert.to_address(token)
        rates, key = await asyncio.gather(
            self.get_address('ExchangeRates', block=block, sync=False),
            self.get_currency_key(token, sync=False)
        )
        if await rates.rateIsStale.coroutine(key, block_identifier=block):
            return None
        try:
            return UsdPrice(await rates.rateForCurrency.coroutine(key, block_identifier=block, decimals=18))
        except Exception as e:
            if not call_reverted(e):
                raise

synthetix = Synthetix(asynchronous=True) if chain.id in addresses else set()
