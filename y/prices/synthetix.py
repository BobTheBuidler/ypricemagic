import logging

from brownie import chain
from cachetools.func import lru_cache, ttl_cache
from eth_abi import encode_single
from y.classes.singleton import Singleton
from y.contracts import Contract, has_method
from y.exceptions import UnsupportedNetwork
from y.networks import Network
from y.utils.multicall import fetch_multicall


logger = logging.getLogger(__name__)

addresses = {
    Network.Mainnet: '0x823bE81bbF96BEc0e25CA13170F5AaCb5B79ba83',
}


class Synthetix(metaclass=Singleton):
    def __init__(self):
        if chain.id not in addresses:
            raise UnsupportedNetwork("synthetix is not supported on this network")

        self.synths = self.load_synths()
        logger.info(f'loaded {len(self.synths)} synths')

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

    def load_synths(self):
        """
        Get target addresses of all synths.
        """
        proxy_erc20 = self.get_address('ProxyERC20')
        return fetch_multicall(
            *[
                [proxy_erc20, 'availableSynths', i]
                for i in range(proxy_erc20.availableSynthCount())
            ]
        )

    @lru_cache(maxsize=None)
    def __contains__(self, token: str) -> bool:
        """
        Check if a token is a synth.
        """
        target = has_method(token, 'target()(address)', return_response=True)
        return target and target in self.synths and Contract(target).proxy() == token

    @lru_cache(maxsize=None)
    def get_currency_key(self, token):
        target = Contract(token).target()
        return Contract(target).currencyKey()

    @ttl_cache(maxsize=None, ttl=600)
    def get_price(self, token, block=None):
        """
        Get a price of a synth in dollars.
        """
        rates = self.get_address('ExchangeRates')
        key = self.get_currency_key(token)
        try:
            return rates.rateForCurrency(key, block_identifier=block) / 1e18
        except ValueError:
            return None


try: synthetix = Synthetix()
except UnsupportedNetwork: synthetix = set()
