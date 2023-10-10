# async: done

import asyncio
import logging
from typing import Optional

from brownie import chain

from y.classes.common import ERC20
from y.constants import wbtc, weth
from y.contracts import Contract
from y.exceptions import NonStandardERC20
from y.networks import Network
from y.prices.lending.aave import aave
from y.prices.lending.compound import CToken
from y.prices.stable_swap.curve import CurvePool
from y.prices.utils.buckets import check_bucket
from y.prices.yearn import YearnInspiredVault

logger = logging.getLogger(__name__)

# This module is far from perfect, but provides an acceptable way to validate some of the prices returned by `get_price`

acceptable_all_chains = [
    weth.address,
    wbtc.address,
]
ACCEPTABLE_HIGH_PRICES = {
    Network.Mainnet: [
        # eth and eth-like
        "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE", # eth
        "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0", # wsteth
        "0xA3D87FffcE63B53E0d54fAa1cc983B7eB0b74A9c", # ecrv
        "0xaA17A236F2bAdc98DDc0Cf999AbB47D47Fc0A6Cf", # ankrcrv
        "0x53a901d48795C58f485cBB38df08FA96a24669D5", # rcrv
        "0xC4C319E2D4d66CcA4464C0c2B32c9Bd23ebe784e", # alETH+ETH-f
        "0x06325440D014e39736583c165C2963BA99fAf14E", # stecrv
        "0x5e74C9036fb86BD7eCdcb084a0673EFc32eA31cb", # sETH
        "0xae78736Cd615f374D3085123A210448E74Fc6393", # rETH
        "0xE95A203B1a91a908F9B9CE46459d101078c2c3cb", # aETHc
        "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84", # stETH
        "0x9559Aaa82d9649C7A7b220E7c461d2E74c9a3593", # rETH
        "0x836A808d4828586A69364065A1e064609F5078c7", # pETH
        "0xc3D088842DcF02C13699F936BB83DFBBc6f721Ab", # vETH
        "0xC1330aCBbcE97cb9695B7ee161c0F95B875a8b0F", # onETH
        "0x5E8422345238F34275888049021821E8E08CAa1f", # fxsETH
        "0x856c4Efb76C1D1AE02e20CEB03A2A6a08b0b8dC3", # OETH
        "0xE72B141DF173b999AE7c1aDcbF60Cc9833Ce56a8", # ETH+
        "0x3d1E5Cf16077F349e999d6b21A4f646e83Cd90c5", # dETH
        "0x0100546F2cD4C9D97f798fFC9755E47865FF7Ee6", # alETH
        "0xBe9895146f7AF43049ca1c1AE358B0541Ea49704", # cbETH
        "0x7C07F7aBe10CE8e33DC6C5aD68FE033085256A84", # icETH
        "0xA35b1B31Ce002FBF2058D22F30f95D405200A15b", # ETHx
        "0x64351fC9810aDAd17A690E4e1717Df5e7e085160", # msETH
        # btc and btc-like
        "0xEB4C2781e4ebA804CE9a9803C67d0893436bB27D", # renbtc
        "0xfE18be6b3Bd88A2D2A7f928d00292E7a9963CfC6", # sbtc
        "0x49849C98ae39Fff122806C06791Fa73784FB3675", # crvrenwbtc
        "0x075b1bb99792c9E1041bA13afEf80C91a1e70fB3", # crvrenwsbtc
        "0xb19059ebb43466C323583928285a49f558E572Fd", # hcrv
        "0x64eda51d3Ad40D56b9dFc5554E06F94e1Dd786Fd", # tbtc/sbtcCrv
        "0xDE5331AC4B3630f94853Ff322B66407e0D6331E8", # pBTC/sbtcCRV
        "0x410e3E86ef427e30B9235497143881f717d93c2A", # bBTC/sbtcCRV
        "0x2fE94ea3d5d4a175184081439753DE15AeF9d614", # oBTC/sbtcCRV
        "0x0327112423F3A68efdF1fcF402F6c5CB9f7C33fd", # btc++
        "0x3212b29E33587A00FB1C83346f5dBFA69A458923", # imbtc
        "0x5228a22e72ccC52d415EcFd199F99D0665E7733b", # pbtc
        "0xFbdCA68601f835b27790D98bbb8eC7f05FDEaA9B", # ibbtc/sbtcCRV-f
        "0x0316EB71485b0Ab14103307bf65a021042c6d380", # hbtc
        "0x9BE89D2a4cd102D8Fecc6BF9dA793be995C22541", # bbtc
        "0x8064d9Ae6cDf087b1bcd5BDf3531bD5d8C537a68", # obtc
        "0x8dAEBADE922dF735c38C80C7eBD708Af50815fAa", # tbtc
        "0x8751D4196027d4e6DA63716fA7786B5174F04C15", # wibbtc
        "0x66eFF5221ca926636224650Fd3B9c497FF828F7D", # multiBTC
        "0x18084fbA666a33d37592fA2633fD49a74DD93a88", # tbtc
        # gold tokens
        "0x45804880De22913dAFE09f4980848ECE6EcbAf78", # paxg
        "0x4922a015c4407F87432B179bb209e125432E4a2A", # xaut
        # other
        "0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e", # yfi
        "0x1cEB5cB57C4D4E2b2433641b95Dd330A33185A44", # kp3r
        "0xD5525D397898e5502075Ea5E830d8914f6F0affe", # meme
        "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2", # mkr
        "0x3A283D9c08E8b55966afb64C515f5143cf907611", # crvCVXETH
        "0x23B608675a2B2fB1890d3ABBd85c5775c51691d5", # socks
        "0xcA3d75aC011BF5aD07a98d02f18225F9bD9A6BDF", # crvtricrypto
        "0xc4AD29ba4B3c580e6D59105FFf484999997675Ff", # crv3crypto
        "0xd075e95423C5c4BA1E122CaE0f4CdFA19b82881b", # wPE
        "0xe9F84dE264E91529aF07Fa2C746e934397810334", # sak3
        "0xa1d0E215a23d7030842FC67cE582a6aFa3CCaB83", # yfii
        "0x0fe629d1E84E171f8fF0C1Ded2Cc2221Caa48a3f", # mask
        "0x5F0E628B693018f639D10e4A4F59BD4d8B2B6B44", # white
        "0xdBdb4d16EdA451D0503b854CF79D55697F90c8DF", # alcx
        "0x3aaDA3e213aBf8529606924d8D1c55CbDc70Bf74", # xMON
        "0x892A6f9dF0147e5f079b0993F486F9acA3c87881", # xFUND
        "0x0ab87046fBb341D058F17CBC4c1133F25a20a52f", # gOHM
        "0x97983236bE88107Cc8998733Ef73D8d969c52E37", # sdYFI
        "0x68749665FF8D2d112Fa859AA293F07A622782F38", # XAUt
        "0xf5f5B97624542D72A9E06f04804Bf81baA15e2B4", # crvUSDTWBTCWETH
        "0x7F86Bf177Dd4F3494b841a37e810A34dD56c829B", # crvUSDCWBTCWETH
        "0x2889302a794dA87fBF1D6Db415C1492194663D13", # crvCRVUSDTBTCWSTETH
        # nfts
        "0x641927E970222B10b2E8CDBC96b1B4F427316f16", # meeb
        "0x9cea2eD9e47059260C97d697f82b8A14EfA61EA5", # punk
        "0x269616D549D7e8Eaa82DFb17028d0B212D11232A", # punk (different)
        "0x69BbE2FA02b4D90A944fF328663667DC32786385", # punk-basic
        "0xD70240Dd62F4ea9a6A2416e0073D72139489d2AA", # glyph
        "0x114f1388fAB456c4bA31B1850b244Eedcd024136", # coolcats
        "0xEA47B64e1BFCCb773A0420247C0aa0a3C1D2E5C5", # bayc
    ],
    Network.BinanceSmartChain: [
        # eth and eth-like
        "0x8d0e18c97e5dd8ee2b539ae8cd3a3654df5d79e5", # bweth
        "0xbfF4a34A4644a113E8200D7F1D79b3555f723AfE", # ibeth
        # btc and btc-like
        "0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c", # btcb
        "0x08FC9Ba2cAc74742177e0afC3dC8Aed6961c24e7", # ibbtcb
    ],
    Network.Fantom: [
        # eth and eth-like
        "0xBDC8fd437C489Ca3c6DA3B5a336D11532a532303", # anyeth
        # btc and btc-like
        "0xDBf31dF14B66535aF65AaC99C32e9eA844e14501", # renbtc
        "0x2406dCe4dA5aB125A18295f4fB9FD36a0f7879A2", # anybtc
        # other
        "0x29b0Da86e484E1C0029B56e817912d778aC0EC69", # yfi
        "0xf43Cc235E686d7BC513F53Fbffb61F760c3a1882", # elite
        "0x58e57cA18B7A47112b877E31929798Cd3D703b0f", # crv3crypto
    ],
    Network.Avalanche: [
        # btc and btc-like
        "0xDBf31dF14B66535aF65AaC99C32e9eA844e14501", # renbtc
        # other
        "0xd6070ae98b8069de6B494332d1A1a81B6179D960", # bifi
    ],
    Network.Optimism: [
        # eth and eth-like
        "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE", # eth
        "0x9Bcef72be871e61ED4fBbc7630889beE758eb81D", # reth
        "0x1F32b1c2345538c0c6f582fCB022739c4A194Ebb", # wsteth
        "0x6806411765Af15Bddd26f8f544A34cC40cb9838B", # frxeth
        "0x484c2D6e3cDd945a8B2DF735e079178C1036578c", # sfrxeth
        "0x1610e3c85dd44Af31eD7f33a63642012Dca0C5A5", # mseth
        "0x3E29D3A9316dAB217754d13b28646B76607c5f04", # aleth
        "0xE405de8F52ba7559f9df3C368500B6E6ae6Cee49", # seth
        # btc and btc-like
        "0x298B9B95708152ff6968aafd889c6586e9169f1D", # sbtc
        "0x6c84a8f1c29108F47a79964b5Fe888D4f4D0dE40", # tbtc
    ],
    Network.Arbitrum: [
        "0x8e0B8c8BB9db49a46697F3a5Bb8A308e744821D2", # crv3crypto
    ],
    Network.Base: [
        # eth and eth-like
        "0x2Ae3F1Ec7F1F5012CFEab0185bfc7aa3cf0DEc22", # cbeth
        # btc and btc-like
        "0x236aa50979D5f3De3Bd1Eeb40E81137F22ab794b", # tbtc
    ],
}.get(chain.id, []) + acceptable_all_chains

async def _sense_check(
    token_address: str, 
    block: Optional[int],
    price: float
    ):

    # if price is in "normal" range, exit sense check
    if price < 1000:
        return None
    
    # if we've already validated that the token should have a high price, exit sense check
    if token_address in ACCEPTABLE_HIGH_PRICES:
        return None

    # for some token types, its normal to have a crazy high nominal price
    # we can skip the sense check for those
    if await _exit_sense_check(token_address):
        return None

    # proceed with sense check
    price_readable = round(price, 4)
    network = Network.name(chain.id)
    try:
        symbol = await ERC20(token_address, asynchronous=True).symbol
        logger.warning(f'unusually high price (${price_readable}) returned for {symbol} {token_address} on {network} block {block}. This does not necessarily mean that the price is wrong, but you may want to validate the price for yourself before proceeding.')
    except NonStandardERC20:
        logger.warning(f'unusually high price (${price_readable}) returned for {token_address} on {network} block {block}. This does not necessarily mean that the price is wrong, but you may want to validate the price for yourself before proceeding.')


#yLazyLogger(logger)
async def _exit_sense_check(token_address: str) -> bool:
    '''
    For some token types, its normal to have a crazy high nominal price.
    We can skip the sense check for those.
    We can also skip wrapped versions of tokens in `ACCEPTABLE_HIGH_PRICES`.
    '''

    bucket = await check_bucket(token_address, sync=False)

    if bucket in ['uni or uni-like lp', 'balancer pool']:
        return True

    elif bucket == 'curve lp':
        underlyings = await CurvePool(token_address, asynchronous=True).coins
        if questionable_underlyings := [und for und in underlyings if und not in ACCEPTABLE_HIGH_PRICES]:
            return all(await asyncio.gather(*[_exit_sense_check(underlying) for underlying in questionable_underlyings]))
        return True
    
    elif bucket == 'atoken':
        underlying = await aave.underlying(token_address, sync=False)
    elif bucket == 'compound':
        underlying = await CToken(token_address, asynchronous=True).underlying
    elif bucket == 'solidex':
        contract = await Contract.coroutine(token_address)
        underlying = await contract.pool.coroutine()
    elif bucket == 'yearn or yearn-like':
        underlying = await YearnInspiredVault(token_address, asynchronous=True).underlying
    else:
        return False

    return underlying in ACCEPTABLE_HIGH_PRICES or await _exit_sense_check(underlying)
