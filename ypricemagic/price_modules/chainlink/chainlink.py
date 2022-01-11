import logging

from brownie import chain, ZERO_ADDRESS
from cachetools.func import ttl_cache
from ypricemagic.exceptions import UnsupportedNetwork
from ypricemagic.networks import Network
from ypricemagic.utils.contracts import Contract, Singleton
from ypricemagic.price_modules.chainlink.feeds import FEEDS
from ypricemagic.utils.events import decode_logs, get_logs_asap

logger = logging.getLogger(__name__)

DENOMINATIONS = {
    'ETH': '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
    'BTC': '0xbBbBBBBbbBBBbbbBbbBbbbbBBbBbbbbBbBbbBBbB',
    'USD': '0x0000000000000000000000000000000000000348',
}

registries = {
    # https://docs.chain.link/docs/feed-registry/#contract-addresses
    Network.Mainnet: '0x47Fb2585D2C56Fe188D0E6ec628a38b74fCeeeDf',
}


class Chainlink(metaclass=Singleton):
    def __init__(self):
        if chain.id not in registries and len(FEEDS) == 0:
            raise UnsupportedNetwork('chainlink is not supported on this network')

        if chain.id in registries: self.registry = Contract(registries[chain.id])
        
        self.load_feeds()

    def load_feeds(self):
        if chain.id in registries:
            logs = decode_logs(
                get_logs_asap(str(self.registry), [self.registry.topics['FeedConfirmed']])
            )
            self.feeds = {
                log['asset']: log['latestAggregator']
                for log in logs
                if log['denomination'] == DENOMINATIONS['USD']
            }
        else: self.feeds = {}
        # for mainnet, we have some extra feeds to pull in
        # for non-mainnet, we have no registry so must get feeds manually
        self.feeds.update(FEEDS)
        logger.info(f'loaded {len(self.feeds)} feeds')

    def get_feed(self, asset):
        return Contract(self.feeds[asset])

    def __contains__(self, asset):
        return asset in self.feeds

    @ttl_cache(maxsize=None, ttl=600)
    def get_price(self, asset, block=None):
        if asset == ZERO_ADDRESS:
            return None
        try:
            price = self.get_feed(asset).latestAnswer(block_identifier=block) / 1e8
            logger.debug("chainlink -> %s", price)
            return price
        except ValueError:
            return None


chainlink = None
try:
    chainlink = Chainlink()
except UnsupportedNetwork:
    pass
