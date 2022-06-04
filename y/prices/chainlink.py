import logging
from functools import cached_property
from typing import Dict, Optional

from async_lru import alru_cache
from async_property import async_cached_property
from brownie import ZERO_ADDRESS, chain
from multicall import Call
from multicall.utils import await_awaitable, gather
from y import convert
from y.classes.common import ERC20
from y.classes.singleton import Singleton
from y.contracts import Contract
from y.datatypes import Address, AnyAddressType, Block, UsdPrice
from y.exceptions import ContractNotVerified, UnsupportedNetwork
from y.networks import Network
from y.utils.events import create_filter, decode_logs, get_logs_asap_async
from y.utils.logging import yLazyLogger

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

# These are feeds we specify anually in addition to the ones fetched from the registry.
# After selecting for `chain.id`, `FEEDS` will return a dict {token_in: feed_address}
FEEDS = {
    Network.Mainnet: {
        "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599": "0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c",  # wbtc -> BTC
        "0x0316EB71485b0Ab14103307bf65a021042c6d380": "0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c",  # hbtc -> btc
        "0x9BE89D2a4cd102D8Fecc6BF9dA793be995C22541": "0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c",  # bbtc -> btc
        "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2": "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419",  # weth -> ETH
        "0x0100546F2cD4C9D97f798fFC9755E47865FF7Ee6": "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419",  # aleth -> ETH
        "0xdB25f211AB05b1c97D595516F45794528a807ad8": "0xb49f677943BC038e9857d61E7d053CaA2C1734C1",  # eurs -> EUR
        "0x9fcf418B971134625CdF38448B949C8640971671": "0xb49f677943BC038e9857d61E7d053CaA2C1734C1",  # eurn-> EUR
        "0xC581b735A1688071A1746c968e0798D642EDE491": "0xb49f677943BC038e9857d61E7d053CaA2C1734C1",  # eurt -> EUR
        "0xD71eCFF9342A5Ced620049e616c5035F1dB98620": "0xb49f677943BC038e9857d61E7d053CaA2C1734C1",  # seur -> EUR
        "0x1a7e4e63778B4f12a199C062f3eFdD288afCBce8": "0xb49f677943BC038e9857d61E7d053CaA2C1734C1",  # ageur -> EUR
        "0x81d66D255D47662b6B16f3C5bbfBb15283B05BC2": "0x438F81D95761d7036cd2617295827D9d01Cf593f",  # ibzar -> ZAR
        "0xf6b1c627e95bfc3c1b4c9b825a032ff0fbf3e07d": "0xBcE206caE7f0ec07b545EddE332A47C2F75bbeb3",  # sJPY -> JPY
        "0x5555f75e3d5278082200Fb451D1b6bA946D8e13b": "0xBcE206caE7f0ec07b545EddE332A47C2F75bbeb3",  # ibjpy -> JPY
        "0xFAFdF0C4c1CB09d430Bf88c75D88BB46DAe09967": "0x77F9710E7d0A19669A13c055F62cd80d313dF022",  # ibAUD -> AUD
        "0x95dFDC8161832e4fF7816aC4B6367CE201538253": "0x01435677fb11763550905594a16b645847c1d0f3",  # ibKRW -> KRW
        "0x69681f8fde45345C3870BCD5eaf4A05a60E7D227": "0x5c0Ab2d9b5a7ed9f470386e82BB36A3613cDd4b5",  # ibGBP -> GBP
        "0x1CC481cE2BD2EC7Bf67d1Be64d4878b16078F309": "0x449d117117838fFA61263B61dA6301AA2a88B13A",  # ibCHF -> CHF
        "0x9AFb950948c2370975fb91a441F36FDC02737cD4": "0x1A31D42149e82Eb99777f903C08A2E41A00085d3",  # hFIL -> FIL
        "0x5CAF29fD8efbe4ED0cfc43A8a211B276E9889583": "0x1A31D42149e82Eb99777f903C08A2E41A00085d3",  # renFIL -> FIL
        "0xEB4C2781e4ebA804CE9a9803C67d0893436bB27D": "0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c",  # renbtc -> BTC
        "0x1C5db575E2Ff833E46a2E9864C22F4B22E0B37C2": "0xd54B033D48d0475f19c5fccf7484E8A981848501",  # renzec -> ZEC
        "0x459086F2376525BdCebA5bDDA135e4E9d3FeF5bf": "0x9F0F69428F923D6c95B781F89E165C9b2df9789D",  # renbch -> BCH
        "0x3832d2F059E55934220881F831bE501D180671A7": "0x2465CefD3b488BE410b941b1d4b2767088e2A028",  # rendoge -> DOGE
        "0x945Facb997494CC2570096c74b5F66A3507330a1": "0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c",  # mbtc -> BTC
        "0x68749665FF8D2d112Fa859AA293F07A622782F38": "0x214eD9Da11D2fbe465a6fc601a91E62EbEc1a0D6",  # xaut -> xau
        "0xa693B19d2931d498c5B318dF961919BB4aee87a5": "0x8b6d9085f310396C6E4f0012783E9f850eaa8a82",  # ust -> UST
        "0xD46bA6D942050d489DBd938a2C909A5d5039A161": "0xe20CA8D7546932360e37E9D72c1a47334af57706",  # ampl -> AMPL
        "0x13B02c8dE71680e71F0820c996E4bE43c2F57d15": "0x6b54e83f44047d2168a195ABA5e9b768762167b5",  # mqqq -> qqq
        "0xd36932143F6eBDEDD872D5Fb0651f4B72Fd15a84": "0x139C8512Cde1778e9b9a8e721ce1aEbd4dD43587",  # maapl -> aapl
        "0x4e840AADD28DA189B9906674B4Afcb77C128d9ea": "0x8c110B94C5f1d347fAcF5E1E938AB2db60E3c9a8",  # anyspell -> spell
        "0xdeFA4e8a7bcBA345F687a2f1456F5Edd9CE97202": "0xf8fF43E991A81e6eC886a3D281A2C6cC19aE70Fc",  # knc -> knc
        "0xEa5A82B35244d9e5E48781F00b11B14E627D2951": "0xDC4BDB458C6361093069Ca2aD30D74cc152EdC75",  # atom -> atom
    },
    Network.BinanceSmartChain: {
        "0xfCe146bF3146100cfe5dB4129cf6C82b0eF4Ad8c": "0x264990fbd0A4796A3E3d8E37C4d5F87a3aCa5Ebf",  # renbtc -> BTC
        "0xA164B067193bd119933e5C1e7877421FCE53D3E5": "0x43d80f616DAf0b0B42a928EeD32147dC59027D41",  # renbch -> BCH
        "0xDBf31dF14B66535aF65AaC99C32e9eA844e14501": "0xE5dbFD9003bFf9dF5feB2f4F445Ca00fb121fb83",  # renfil -> FIL
        "0xc3fEd6eB39178A541D274e6Fc748d48f0Ca01CC3": "0x3AB0A0d137D4F946fBB19eecc6e92E64660231C8",  # rendoge -> DOGE
    },
    Network.Polygon: {
        "0x4c28f48448720e9000907BC2611F73022fdcE1fA": "0xF9680D99D6C9589e2a93a78A04A279e509205945",  # weth -> ETH
        "0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6": "0xc907E116054Ad103354f2D350FD2514433D57F6f",  # wbtc -> BTC
        "0xb33EaAd8d922B1083446DC23f610c2567fB5180f": "0xdf0Fb4e4F928d2dCB76f438575fDD8682386e13C",  # uni -> UNI
        "0xDBf31dF14B66535aF65AaC99C32e9eA844e14501": "0xc907E116054Ad103354f2D350FD2514433D57F6f",  # renbtc -> BTC
        "0x0694bf58a4F48C5970454CD4874218eBa843Cf3e": "0xF9680D99D6C9589e2a93a78A04A279e509205945",  # reneth -> ETH
        "0xc3fEd6eB39178A541D274e6Fc748d48f0Ca01CC3": "0x327d9822e9932996f55b39F557AEC838313da8b7",  # renbch -> BCH
        "0x31a0D1A199631D244761EEba67e8501296d2E383": "0xBC08c639e579a391C4228F20d0C29d0690092DF0",  # renzec -> ZEC
        "0xcE829A89d4A55a63418bcC43F00145adef0eDB8E": "0xbaf9327b6564454F4a3364C33eFeEf032b4b4444",  # rendoge -> DOGE
        "0x7c7DAAF2dB46fEFd067f002a69FD0BE14AeB159f": "0x1248573D9B62AC86a3ca02aBC6Abe6d403Cd1034",  # renluna -> LUNA
        "0x6E48a0c5386211837d99DacA233f45EF5aa5f594": "0xfE4A8cc5b5B2366C1B58Bea3858e81843581b2F7",  # renusdc -> USDC
        "0xf55941e971302C634c586416c43469F3EaD5ad3e": "0x0A6513e40db6EB1b165753AD52E80663aeA50545",  # renusdt -> USDT
        "0x7BDF330f423Ea880FF95fC41A280fD5eCFD3D09f": "0x73366Fe0AA0Ded304479862808e02506FE556a98",  # eurt -> EUR
        "0x4e3Decbb3645551B8A19f0eA1678079FCB33fB4c": "0x73366Fe0AA0Ded304479862808e02506FE556a98",  # jeur -> EUR
        "0xE0B52e49357Fd4DAf2c15e02058DCE6BC0057db4": "0x73366Fe0AA0Ded304479862808e02506FE556a98",  # ageur -> EUR
        "0x8343091F2499FD4b6174A46D067A920a3b851FF9": "0xD647a6fC9BC6402301583C91decC5989d8Bc382D",  # jjpy -> JPY
        "0x6AE7Dfc73E0dDE2aa99ac063DcF7e8A63265108c": "0xD647a6fC9BC6402301583C91decC5989d8Bc382D",  # jpyc -> JPY
    },
    Network.Fantom: {
        "0xDBf31dF14B66535aF65AaC99C32e9eA844e14501": "0x8e94C22142F4A64b99022ccDd994f4e9EC86E4B4",  # renbtc -> BTC
        "0x0694bf58a4F48C5970454CD4874218eBa843Cf3e": "0x11DdD3d147E5b83D01cee7070027092397d63658",  # reneth -> ETH
        "0xd82a4f018eCF6be6E991C3c4a160C9758EC3338F": "0xf8f57321c2e3E202394b0c0401FD6392C3e7f465",  # renbusd -> BUSD
        "0xf55941e971302C634c586416c43469F3EaD5ad3e": "0xF64b636c5dFe1d3555A847341cDC449f612307d0",  # renusdt -> USDT
        "0x6E48a0c5386211837d99DacA233f45EF5aa5f594": "0x2553f4eeb82d5A26427b8d1106C51499CBa5D99c",  # renusdc -> USDC
    },
    Network.Avalanche: {
        "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7": "0x0A77230d17318075983913bC2145DB16C7366156",  # wavax -> AVAX
        "0x408D4cD0ADb7ceBd1F1A1C33A0Ba2098E1295bAB": "0x2779D32d5166BAaa2B2b658333bA7e6Ec0C65743",  # wbtc -> BTC
        "0x50b7545627a5162F82A992c33b87aDc75187B218": "0x2779D32d5166BAaa2B2b658333bA7e6Ec0C65743",  # wbtc.e -> btc
        "0xf20d962a6c8f70c731bd838a3a388D7d48fA6e15": "0x976B3D034E162d8bD72D6b9C989d545b839003b0",  # eth -> eth
        "0x49D5c2BdFfac6CE2BFdB6640F4F80f226bc10bAB": "0x976B3D034E162d8bD72D6b9C989d545b839003b0",  # weth.e -> eth
        "0x39cf1BD5f15fb22eC3D9Ff86b0727aFc203427cc": "0x449A373A090d8A1e5F74c63Ef831Ceff39E94563",  # sushi -> sushi
        "0xf39f9671906d8630812f9d9863bBEf5D523c84Ab": "0x9a1372f9b1B71B3A5a72E092AE67E172dBd7Daaa",  # uni -> uni
        "0x8eBAf22B6F053dFFeaf46f4Dd9eFA95D89ba8580": "0x9a1372f9b1B71B3A5a72E092AE67E172dBd7Daaa",  # uni.e -> uni
        "0xB3fe5374F67D7a22886A0eE082b2E2f9d2651651": "0x49ccd9ca821EfEab2b98c60dC60F518E765EDe9a",  # link -> link
        "0x5947BB275c521040051D82396192181b413227A3": "0x49ccd9ca821EfEab2b98c60dC60F518E765EDe9a",  # link.e -> link
        "0xDBf31dF14B66535aF65AaC99C32e9eA844e14501": "0x2779D32d5166BAaa2B2b658333bA7e6Ec0C65743",  # renbtc -> BTC
        "0xc4Ace9278e7E01755B670C0838c3106367639962": "0x2F194315f122d374a27973e259783d5C864A5bf6",  # renfil -> FIL
        "0x7c7DAAF2dB46fEFd067f002a69FD0BE14AeB159f": "0x12Fe6A4DF310d4aD9887D27D4fce45a6494D4a4a",  # renluna -> LUNA
        "0x63a72806098Bd3D9520cC43356dD78afe5D386D9": "0x3CA13391E9fb38a75330fb28f8cc2eB3D9ceceED",  # aave.e -> aave
        "0x6e84a6216eA6dACC71eE8E6b0a5B7322EEbC0fDd": "0x02D35d3a8aC3e1626d3eE09A78Dd87286F5E8e3a",  # joe -> joe
        "0xCE1bFFBD5374Dac86a2893119683F4911a2F7814": "0x4F3ddF9378a4865cf4f28BE51E10AECb83B7daeE",  # spell -> spell
        "0x8729438EB15e2C8B576fCc6AeCdA6A148776C0F5": "0x36E039e6391A5E7A7267650979fdf613f659be5D",  # qi -> qi
        "0x027dbcA046ca156De9622cD1e2D907d375e53aa7": "0xcf667FB6Bd30c520A435391c50caDcDe15e5e12f",  # ampl -> ampl
        "0x6E48a0c5386211837d99DacA233f45EF5aa5f594": "0xF096872672F44d6EBA71458D74fe67F9a77a23B9",  # renusdc -> USDC
        "0xf55941e971302C634c586416c43469F3EaD5ad3e": "0xEBE676ee90Fe1112671f19b6B7459bC678B67e8a",  # renusdt -> USDT
        "0xEB9aC3e1C9C3F919804Bdc412e0a39b94D4C09d3": "0x51D7180edA2260cc4F6e4EebB82FEF5c3c2B8300",  # rendai -> DAI
        "0x0694bf58a4F48C5970454CD4874218eBa843Cf3e": "0x976B3D034E162d8bD72D6b9C989d545b839003b0",  # reneth -> ETH
        "0x705Bc47EbA113Be1a66e20824a05a176aA3b5265": "0x54EdAB30a7134A16a54218AE64C73e1DAf48a8Fb",  # renmim -> MIM
    },
    Network.Arbitrum: {
        "0xDBf31dF14B66535aF65AaC99C32e9eA844e14501": "0x6ce185860a4963106506C203335A2910413708e9",  # renbtc -> BTC
        "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1": "0x639Fe6ab55C921f74e7fac1ee960C0B6293ba612",  # weth -> ETH
        "0xD22a58f79e9481D1a88e00c343885A588b34b68B": "0xA14d53bC1F1c0F31B4aA3BD109344E5009051a84",  # eurs -> EUR
    }
}.get(chain.id, {})


class Chainlink(metaclass=Singleton):
    def __init__(self) -> None:
        if chain.id not in registries and len(FEEDS) == 0:
            raise UnsupportedNetwork('chainlink is not supported on this network')

        if chain.id in registries:
            self.registry = Contract(registries[chain.id])
        
    @cached_property
    @yLazyLogger(logger)
    def feeds(self) -> Dict[ERC20, str]:
        return await_awaitable(self.feeds_async)
    
    @yLazyLogger(logger)
    @async_cached_property
    async def feeds_async(self) -> Dict[ERC20, str]:
        if chain.id in registries:
            try:
                log_filter = create_filter(str(self.registry), [self.registry.topics['FeedConfirmed']])
                new_entries = log_filter.get_new_entries()
            except ValueError as e:
                if 'the method is currently not implemented: eth_newFilter' not in str(e):
                    raise
                new_entries = await get_logs_asap_async(str(self.registry), [self.registry.topics['FeedConfirmed']])

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

    @yLazyLogger(logger)
    def get_feed(self, asset: Address) -> Optional[Contract]:
        return await_awaitable(self.get_feed_async(asset))
    
    @yLazyLogger(logger)
    async def get_feed_async(self, asset: Address) -> Optional[Contract]:
        feeds = await self.feeds_async
        try:
            return Contract(feeds[convert.to_address(asset)])
        except ContractNotVerified:
            return None

    @yLazyLogger(logger)
    def __contains__(self, asset: AnyAddressType) -> bool:
        return convert.to_address(asset) in self.feeds
    
    async def has_feed(self, asset: AnyAddressType) -> bool:
        return convert.to_address(asset) in await self.feeds_async

    def get_price(self, asset, block: Optional[Block] = None) -> UsdPrice:
        return await_awaitable(self.get_price_async(asset, block))

    @yLazyLogger(logger)
    async def get_price_async(self, asset, block: Optional[Block] = None) -> UsdPrice:
        if block is None:
            block = chain.height
        return await self._get_price_async(asset, block)

    @alru_cache(maxsize=None)
    async def _get_price_async(self, asset, block: Block) -> Optional[UsdPrice]:
        asset = convert.to_address(asset)
        if asset == ZERO_ADDRESS:
            return None
        feed = await self.get_feed_async(asset)
        if feed is None:
            return None
        try:
            latest_answer, scale = await gather([
                Call(feed.address, 'latestAnswer()(uint)', block_id=block).coroutine(),
                self.feed_scale_async(asset),
            ])
        except ValueError as e:
            print(feed.address)
            print(str(e))
            return None

        if latest_answer:
            price = latest_answer / scale
            return price
    
    def feed_decimals(self, asset: AnyAddressType) -> int:
        return await_awaitable(self.feed_decimals_async(asset))

    @yLazyLogger(logger)
    @alru_cache(maxsize=None)
    async def feed_decimals_async(self, asset: AnyAddressType) -> int:
        asset = convert.to_address(asset)
        feed = await self.get_feed_async(asset)
        return await Call(feed.address, ['decimals()(uint)'], []).coroutine()
    
    def feed_scale(self, asset: AnyAddressType) -> int:
        return await_awaitable(self.feed_scale_async(asset))

    async def feed_scale_async(self, asset: AnyAddressType) -> int:
        return 10 ** await self.feed_decimals_async(asset)


try: chainlink = Chainlink()
except UnsupportedNetwork: chainlink = set()
