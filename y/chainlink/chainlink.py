import logging
from functools import cached_property
from typing import Dict

from brownie import ZERO_ADDRESS, chain, convert
from cachetools.func import ttl_cache
from y.chainlink.feeds import FEEDS
from y.classes.common import ERC20
from y.classes.singleton import Singleton
from y.contracts import Contract
from y.decorators import log
from y.exceptions import UnsupportedNetwork
from y.networks import Network
from y.utils.events import create_filter, decode_logs, get_logs_asap

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

        if chain.id in registries:
            self.registry = Contract(registries[chain.id])
        
    @cached_property
    @log(logger)
    def feeds(self) -> Dict[ERC20, str]:
        if chain.id in registries:
            try:
                log_filter = create_filter(str(self.registry), [self.registry.topics['FeedConfirmed']])
                new_entries = log_filter.get_new_entries()
            except ValueError as e:
                if 'the method is currently not implemented: eth_newFilter' not in str(e):
                    raise
                new_entries = get_logs_asap(str(self.registry), [self.registry.topics['FeedConfirmed']])

            logs = decode_logs(new_entries)
            feeds = {
                log['asset']: log['latestAggregator']
                for log in logs
                if log['denomination'] == DENOMINATIONS['USD'] and log['latestAggregator'] != ZERO_ADDRESS
            }
        else: feeds = {}
        # for mainnet, we have some extra feeds to pull in
        # for non-mainnet, we have no registry so must get feeds manually
        feeds.update(FEEDS)
        feeds = {ERC20(token): feed for token, feed in feeds.items()}
        logger.info(f'loaded {len(feeds)} feeds')
        return feeds

    @log(logger)
    def get_feed(self, asset):
        return Contract(self.feeds[asset])

    @log(logger)
    def __contains__(self, asset):
        return convert.to_address(asset) in self.feeds

    @ttl_cache(maxsize=None, ttl=600)
    @log(logger)
    def get_price(self, asset, block=None):
        if asset == ZERO_ADDRESS:
            return None
        try:
            price = self.get_feed(asset).latestAnswer(block_identifier=block) / 1e8
            logger.debug("chainlink -> %s", price)
            return price
        except ValueError:
            return None


try: chainlink = Chainlink()
except UnsupportedNetwork: chainlink = set()
