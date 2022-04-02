import logging
from functools import cached_property
from typing import List, Optional

from brownie import chain
from brownie.convert.datatypes import EthAddress, HexString
from cachetools.func import lru_cache
from eth_abi import encode_single
from multicall import Call
from y import convert
from y.classes.singleton import Singleton
from y.contracts import Contract, has_method
from y.datatypes import UsdPrice
from y.exceptions import UnsupportedNetwork
from y.networks import Network
from y.typing import Address, AnyAddressType, Block
from y.utils.multicall import fetch_multicall

logger = logging.getLogger(__name__)

addresses = {
    Network.Mainnet: '0x823bE81bbF96BEc0e25CA13170F5AaCb5B79ba83',
}


class Synthetix(metaclass=Singleton):
    def __init__(self) -> None:
        if chain.id not in addresses:
            raise UnsupportedNetwork("synthetix is not supported on this network")

    @lru_cache(maxsize=None)
    def get_address(self, name) -> Contract:
        """
        Get contract from Synthetix registry.
        See also https://docs.synthetix.io/addresses/
        """
        address_resolver = Contract(addresses[chain.id])
        address = address_resolver.getAddress(encode_single('bytes32', name.encode()))
        proxy = Contract(address)
        return Contract(proxy.target()) if hasattr(proxy, 'target') else proxy

    @cached_property
    def synths(self) -> List[EthAddress]:
        """
        Get target addresses of all synths.
        """
        proxy_erc20 = self.get_address('ProxyERC20')
        synths = fetch_multicall(
            *[
                [proxy_erc20, 'availableSynths', i]
                for i in range(proxy_erc20.availableSynthCount())
            ]
        )
        logger.info(f'loaded {len(synths)} synths')
        return synths

    def __contains__(self, token: AnyAddressType) -> bool:
        """
        Check if a token is a synth.
        """
        token = convert.to_address(token)
        if synthetix.get_currency_key(token):
            return True
        if has_method(token, 'target()(address)'):
            target = Call(token.address, 'target()(address)')()
            return target in synthetix.synths and Call(target, 'proxy()(address)')() == token
        return False

    @lru_cache(maxsize=None)
    def get_currency_key(self, token: Address) -> Optional[HexString]:
        target = Call(token, ['target()(address)'])() if Contract(token).has_method('target()(address)') else token
        return Call(target, ['currencyKey()(bytes32)'])() if Contract(target).has_method('currencyKey()(bytes32)') else None

    def get_price(self, token: AnyAddressType, block: Optional[Block] = None) -> Optional[UsdPrice]:
        """
        Get a price of a synth in dollars.
        """
        token = convert.to_address(token)
        rates = self.get_address('ExchangeRates')
        key = self.get_currency_key(token)
        try:
            return UsdPrice(rates.rateForCurrency(key, block_identifier=block) / 1e18)
        except ValueError:
            return None


try:
    synthetix = Synthetix()
except UnsupportedNetwork:
    synthetix = set()
