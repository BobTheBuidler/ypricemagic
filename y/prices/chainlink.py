import logging
from typing import AsyncIterator, Optional

import a_sync
import dank_mids
from y import time
from async_lru import alru_cache
from brownie import ZERO_ADDRESS
from brownie.network.event import _EventItem
from multicall import Call
from web3.exceptions import ContractLogicError

from y import ENVIRONMENT_VARIABLES as ENVS
from y import convert
from y._decorators import stuck_coro_debugger
from y.classes.common import ERC20
from y.constants import CHAINID
from y.contracts import Contract, contract_creation_block_async
from y.datatypes import Address, AnyAddressType, Block, UsdPrice
from y.exceptions import UnsupportedNetwork
from y.networks import Network
from y.utils.cache import a_sync_ttl_cache
from y.utils.events import ProcessedEvents

logger = logging.getLogger(__name__)

DENOMINATIONS = {
    "ETH": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
    "BTC": "0xbBbBBBBbbBBBbbbBbbBbbbbBBbBbbbbBbBbbBBbB",
    "USD": "0x0000000000000000000000000000000000000348",
}

registries = {
    # https://docs.chain.link/docs/feed-registry/#contract-addresses
    Network.Mainnet: "0x47Fb2585D2C56Fe188D0E6ec628a38b74fCeeeDf",
}

# These are feeds we specify anually in addition to the ones fetched from the registry.
# After selecting for `CHAINID`, `FEEDS` will return a dict {token_in: feed_address}
FEEDS = {
    Network.Mainnet: {
        "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599": "0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c",  # wbtc -> BTC
        "0xfE18be6b3Bd88A2D2A7f928d00292E7a9963CfC6": "0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c",  # sbtc -> BTC
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
        "0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83": "0xf4766552D15AE4d256Ad41B6cf2933482B0680dc",  # wftm -> FTM
        "0x321162Cd933E2Be498Cd2267a90534A804051b11": "0x8e94C22142F4A64b99022ccDd994f4e9EC86E4B4",  # wbtc -> BTC
        "0x2406dCe4dA5aB125A18295f4fB9FD36a0f7879A2": "0x8e94C22142F4A64b99022ccDd994f4e9EC86E4B4",  # anybtc -> BTC
        "0xDBf31dF14B66535aF65AaC99C32e9eA844e14501": "0x8e94C22142F4A64b99022ccDd994f4e9EC86E4B4",  # renbtc -> BTC
        "0x74b23882a30290451A17c44f4F05243b6b58C76d": "0x11DdD3d147E5b83D01cee7070027092397d63658",  # weth -> ETH
        "0xBDC8fd437C489Ca3c6DA3B5a336D11532a532303": "0x11DdD3d147E5b83D01cee7070027092397d63658",  # anyeth -> ETH
        "0x0694bf58a4F48C5970454CD4874218eBa843Cf3e": "0x11DdD3d147E5b83D01cee7070027092397d63658",  # reneth -> ETH
        "0xd6070ae98b8069de6B494332d1A1a81B6179D960": "0x4F5Cc6a2291c964dEc4C7d6a50c0D89492d4D91B",  # bifi -> BIFI
        "0x1E4F97b9f9F913c46F1632781732927B9019C68b": "0xa141D7E3B44594cc65142AE5F2C7844Abea66D2B",  # crv -> CRV
        "0x6a07A792ab2965C72a5B8088d3a069A7aC3a993B": "0xE6ecF7d2361B6459cBb3b4fb065E0eF4B175Fe74",  # aave -> AAVE
        "0x657A1861c15A3deD9AF0B6799a195a249ebdCbc6": "0xD2fFcCfA0934caFdA647c5Ff8e7918A10103c01c",  # cream -> CREAM
        "0xb3654dc3D10Ea7645f8319668E8F54d2574FBdC8": "0x221C773d8647BC3034e91a0c47062e26D20d97B4",  # link -> LINK
        "0x399fe752D39338d28C36F3370fbebd8292fb9E6e": "0xb26867105D25bD127862bEA9B952Fa2E89942837",  # ohmv2 -> OHM
        "0x56ee926bD8c72B2d5fa1aF4d9E4Cbb515a1E3Adc": "0x2Eb00cC9dB7A7E0a013A49b3F6Ac66008d1456F7",  # snx -> SNX
        "0x468003B688943977e6130F4F68F23aad939a1040": "0x02E48946849e0BFDD7bEa5daa80AF77195C7E24c",  # spell -> SPELL
        "0xae75A438b2E0cB8Bb01Ec1E1e376De11D44477CC": "0xCcc059a1a17577676c8673952Dc02070D29e5a66",  # sushi -> SUSHI
        "0x81740D647493a61329E1c574A11ee7577659fb14": "0x4be9c8fb4105380116c03fc2eeb9ea1e1a109d95",  # fchf -> CHF
        "0xe105621721D1293c27be7718e041a4Ce0EbB227E": "0x3E68e68ea2c3698400465e3104843597690ae0f7",  # feur -> EUR
        "0x29b0Da86e484E1C0029B56e817912d778aC0EC69": "0x9B25eC3d6acfF665DfbbFD68B3C1D896E067F0ae",  # yfi -> YFI
        "0xb3654dc3D10Ea7645f8319668E8F54d2574FBdC8": "0x221C773d8647BC3034e91a0c47062e26D20d97B4",  # link -> LINK
        "0xae75A438b2E0cB8Bb01Ec1E1e376De11D44477CC": "0xCcc059a1a17577676c8673952Dc02070D29e5a66",  # sushi -> SUSHI
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
        "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1": "0x639Fe6ab55C921f74e7fac1ee960C0B6293ba612",  # weth -> ETH
        "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f": "0x6ce185860a4963106506C203335A2910413708e9",  # wbtc -> BTC
        "0xDBf31dF14B66535aF65AaC99C32e9eA844e14501": "0x6ce185860a4963106506C203335A2910413708e9",  # renbtc -> BTC
        "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1": "0xc5C8E77B397E531B8EC06BFb0048328B30E9eCfB",  # dai -> DAI
        "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8": "0x50834F3163758fcC1Df9973b6e91f0F0F0434aD3",  # usdc -> USDC
        "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9": "0x3f3f5dF88dC9F13eac63DF89EC16ef6e7E25DdE7",  # usdt -> USDT
        "0xFEa7a6a0B346362BF88A9e4A88416B77a57D6c2A": "0x87121F6c9A9F6E90E59591E4Cf4804873f54A95b",  # mim -> MIM
        "0xD22a58f79e9481D1a88e00c343885A588b34b68B": "0xA14d53bC1F1c0F31B4aA3BD109344E5009051a84",  # eurs -> EUR
        "0x17FC002b466eEc40DaE837Fc4bE5c67993ddBd6F": "0x0809E3d38d1B4214958faf06D8b1B1a2b73f2ab8",  # frax -> FRAX
        "0xFa247d0D55a324ca19985577a2cDcFC383D87953": "0xfF82AAF635645fD0bcc7b619C3F28004cDb58574",  # php -> PHP
        "0x82e3A8F066a6989666b031d916c43672085b1582": "0x745Ab5b69E01E2BE1104Ca84937Bb71f96f5fB21",  # yfi -> YFI
    },
    Network.Optimism: {
        "0x68f180fcCe6836688e9084f035309E29Bf0A2095": "0xD702DD976Fb76Fffc2D3963D037dfDae5b04E593",  # wbtc -> BTC
        "0x298B9B95708152ff6968aafd889c6586e9169f1D": "0xD702DD976Fb76Fffc2D3963D037dfDae5b04E593",  # sbtc -> BTC
        "0x4200000000000000000000000000000000000006": "0x13e3Ee699D1909E989722E753853AE30b17e08c5",  # weth -> ETH
        "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1": "0x8dBa75e83DA73cc766A7e5a0ee71F656BAb470d6",  # dai -> DAI
        "0x4200000000000000000000000000000000000042": "0x0D276FC14719f9292D5C1eA2198673d1f4269246",  # op -> OP
        "0x2E3D870790dC77A83DD1d18184Acc7439A53f475": "0xc7D132BeCAbE7Dcc4204841F33bae45841e41D9C",  # frax -> FRAX
        "0x350a791Bfc2C21F9Ed5d10980Dad2e2638ffa7f6": "0xCc232dcFAAE6354cE191Bd574108c1aD03f86450",  # link -> LINK
        "0x7F5c764cBc14f9669B88837ca1490cCa17c31607": "0x16a9FA2FDa030272Ce99B29CF780dFA30361E0f3",  # usdc -> USDC
        "0x8700dAec35aF8Ff88c16BdF0418774CB3D7599B4": "0x2FCF37343e916eAEd1f1DdaaF84458a359b53877",  # snx -> SNX
        "0x3c8B650257cFb5f272f799F5e2b4e65093a11a05": "0x0f2Ed59657e391746C1a097BDa98F2aBb94b1120",  # velo -> VELO
    },
    Network.Base: {
        "0x4200000000000000000000000000000000000006": "0x71041dddad3595F9CEd3DcCFBe3D1F4b0a16Bb70",  # weth -> ETH
        "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb": "0x591e79239a7d679378eC8c847e5038150364C78F",  # dai -> DAI
    },
}.get(CHAINID, {})

ONE_DAY = 24 * 60 * 60


class Feed:
    __slots__ = (
        "address",
        "asset",
        "latest_answer",
        "latest_timestamp",
        "start_block",
        "_stale_thru_block",
    )

    def __init__(
        self,
        address: AnyAddressType,
        asset: AnyAddressType,
        start_block: int = 0,
        *,
        asynchronous: bool = False,
    ):
        self.address = convert.to_address(address)
        self.asset = ERC20(asset, asynchronous=asynchronous)
        self.start_block = start_block
        # we could make less calls by using latestRoundData but then we have to repeatedly decode a bunch of useless data
        self.latest_answer = Call(self.address, "latestAnswer()(int256)").coroutine
        self.latest_timestamp = Call(
            self.address, "latestTimestamp()(uint256)"
        ).coroutine
        self._stale_thru_block = None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} address={self.address} asset={self.asset}>"

    @property
    def contract(self) -> Contract:
        return Contract(self.address)

    # @a_sync.future
    async def decimals(self) -> int:
        return await Call(self.address, "decimals()(uint)")

    # @a_sync.future(cache_type='memory')
    @alru_cache(maxsize=None)
    async def scale(self) -> Optional[int]:
        return await (10 ** a_sync.ASyncFuture(self.decimals()))

    # @a_sync.future
    @stuck_coro_debugger
    async def get_price(self, block: int) -> Optional[UsdPrice]:
        """Get the price of the asset at a specific block.

        If the feed is stale, it returns None.

        Args:
            block: The block number to get the price for.

        Examples:
            >>> feed = Feed("0xAddress", "0xAsset")
            >>> price = await feed.get_price(12345678)
            >>> print(price)

        Returns:
            The price of the asset in USD, or None if the feed is stale.
        """
        if self._stale_thru_block and self._stale_thru_block > block:
            logger.debug("%s is stale, must fetch price from elsewhere", self)
            return None

        try:
            updated_at = await self.latest_timestamp(block_id=block)
        except ContractLogicError:
            return None

        if updated_at + ONE_DAY < await time.get_block_timestamp_async(block):
            # if 24h have passed since last feed update, we can't trust it
            # NOTE: is there a way to tell on chain if a feed is retired? I haven't yet seen one go stale and come back
            logger.debug("%s is stale, must fetch price from elsewhere", self)
            if self._stale_thru_block is None or block > self._stale_thru_block:
                self._stale_thru_block = block
            return None

        latest_answer = await self.latest_answer(block_id=block)
        logger.debug("latest_answer: %s", latest_answer)
        # NOTE: just playing with smth here
        scale = a_sync.ASyncFuture(self.scale())
        price = latest_answer / scale
        try:
            price = UsdPrice(await price)
        except ContractLogicError as e:
            if "execution reverted" not in str(e):
                raise
            price = None
        logger.debug("%s price at %s: %s", self, block, price)
        return price


class FeedsFromEvents(ProcessedEvents[Feed]):
    __slots__ = ("asynchronous",)

    def __init__(self, addresses, topics, *, asynchronous: bool = True):
        self.asynchronous = asynchronous
        super().__init__(addresses=addresses, topics=topics)

    @staticmethod
    def _include_event(event: _EventItem) -> bool:
        """
        Determine whether to include a given event in this container.

        Args:
            event: The event.

        Returns:
            True if the event should be included, False otherwise.

        Examples:
            >>> processed_events = ProcessedEvents(addresses=["0x1234..."], topics=["0x5678..."])
            >>> include = FeedsFromEvents._include_event(event)
            >>> print(include)
        """
        return (
            event["denomination"] == DENOMINATIONS["USD"]
            and event["latestAggregator"] != ZERO_ADDRESS
        )

    def _process_event(self, event: _EventItem) -> Feed:
        return Feed(
            event["latestAggregator"],
            event["asset"],
            event.block_number,
            asynchronous=self.asynchronous,
        )

    def _get_block_for_obj(self, obj: Feed) -> int:
        return obj.start_block


class Chainlink(a_sync.ASyncGenericBase):
    def __init__(self, *, asynchronous: bool = True) -> None:
        """Initialize the Chainlink class.

        Args:
            asynchronous: Whether to use asynchronous operations.

        Raises:
            UnsupportedNetwork: If Chainlink is not supported on the current network.

        Examples:
            >>> chainlink = Chainlink(asynchronous=True)
        """
        super().__init__()
        self.asynchronous = asynchronous
        self._feeds = [
            Feed(feed, asset, asynchronous=self.asynchronous)
            for asset, feed in FEEDS.items()
        ]
        if CHAINID in registries:
            self.registry = Contract(registries[CHAINID])
            self._feeds_from_events = FeedsFromEvents(
                addresses=str(self.registry),
                topics=[self.registry.topics["FeedConfirmed"]],
                asynchronous=asynchronous,
            )
        elif len(FEEDS) == 0:
            raise UnsupportedNetwork("chainlink is not supported on this network")
        else:
            self.registry = None
            self._feeds_from_events = None

    async def _feeds_thru_block(self, block: int) -> AsyncIterator[Feed]:
        """Yield feeds up to a specific block.

        Args:
            block: The block number to yield feeds up to.

        Yields:
            Feeds available up to the specified block.

        Examples:
            >>> async for feed in chainlink._feeds_thru_block(12345678):
            ...     print(feed)
        """
        for feed in self._feeds:
            yield feed
        if self._feeds_from_events:
            async for feed in self._feeds_from_events.objects(to_block=block):
                yield feed

    @a_sync_ttl_cache
    async def get_feed(self, asset: Address) -> Optional[Feed]:
        """Get the feed for a specific asset.

        Args:
            asset: The address of the asset.

        Examples:
            >>> feed = await chainlink.get_feed("0xAsset")
            >>> print(feed)

        Returns:
            The feed for the specified asset, or None if not found.
        """
        asset = await convert.to_address_async(asset)
        async for feed in self._feeds_thru_block(await dank_mids.eth.block_number):
            if asset == feed.asset:
                return feed

    async def has_feed(self, asset: AnyAddressType) -> bool:
        """Check if a feed exists for a specific asset.

        Args:
            asset: The address of the asset.

        Examples:
            >>> has_feed = await chainlink.has_feed("0xAsset")
            >>> print(has_feed)

        Returns:
            True if a feed exists for the specified asset, False otherwise.
        """
        # NOTE: we avoid using `get_feed` here so we don't needlessly fill the cache with Nones
        asset = convert.to_address(asset)
        async for feed in self._feeds_thru_block(await dank_mids.eth.block_number):
            if asset == feed.asset:
                return True
        return False

    # @a_sync.future
    @stuck_coro_debugger
    async def get_price(
        self, asset: AnyAddressType, block: Optional[Block] = None
    ) -> Optional[UsdPrice]:
        """Get the price of an asset at a specific block.

        If the block is not specified, it uses the latest block.

        Args:
            asset: The address of the asset.
            block: The block number to get the price for.

        Examples:
            >>> price = await chainlink.get_price("0xAsset", 12345678)
            >>> print(price)

        Returns:
            The price of the asset in USD, or None if the price cannot be fetched.

        See Also:
            - :meth:`get_feed`
        """
        if block is None:
            block = await dank_mids.eth.block_number
        logger.debug("getting price for %s at %s", asset, block)
        return await self._get_price(str(asset), block)  # force to string for cache key

    @alru_cache(maxsize=1000, ttl=ENVS.CACHE_TTL)
    async def _get_price(self, asset: Address, block: Block) -> Optional[UsdPrice]:
        asset = convert.to_address(asset)
        if asset == ZERO_ADDRESS:
            return None
        feed: Feed
        feed = await self.get_feed(asset, sync=False)
        if feed is None:
            return
        if block is not None and block < await contract_creation_block_async(
            feed.address, True
        ):
            return
        try:
            return await feed.get_price(block=block)
        except (TypeError, ValueError) as e:
            logger.debug("error for feed %s: %s", feed, e)


try:
    chainlink = Chainlink(asynchronous=True)
except UnsupportedNetwork:
    chainlink = set()
