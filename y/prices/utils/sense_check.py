# async: done

import logging

from brownie import chain

from y.classes.common import ERC20
from y.constants import wbtc, weth
from y.networks import Network
from y.prices.utils.buckets import check_bucket_async
from y.utils.logging import yLazyLogger
from y.utils.raw_calls import raw_call_async

logger = logging.getLogger(__name__)

# This module is far from perfect, but provides an acceptable way to validate some of the prices returned by `get_price`

ACCEPTABLE_HIGH_PRICES = {
    Network.Mainnet: [
        # eth and eth-like
        "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE", # eth
        weth.address,
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
        # btc and btc-like
        wbtc.address,
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
        weth.address,
        "0x8d0e18c97e5dd8ee2b539ae8cd3a3654df5d79e5", # bweth
        "0xbfF4a34A4644a113E8200D7F1D79b3555f723AfE", # ibeth
        # btc and btc-like
        wbtc.address,
        "0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c", # btcb
        "0x08FC9Ba2cAc74742177e0afC3dC8Aed6961c24e7", # ibbtcb
    ],
    Network.Polygon: [
        # eth and eth-like
        weth.address,
        # btc and btc-like
        wbtc.address,
    ],
    Network.Fantom: [
        # eth and eth-like
        weth.address,
        # btc and btc-like
        wbtc.address,
        # other
        "0x29b0Da86e484E1C0029B56e817912d778aC0EC69", # yfi
    ],
    Network.Avalanche: [
        # eth and eth-like
        weth.address,
        # btc and btc-like
        wbtc.address,
        "0xDBf31dF14B66535aF65AaC99C32e9eA844e14501", # renbtc

        "0xd6070ae98b8069de6B494332d1A1a81B6179D960", # bifi
    ],
    Network.Arbitrum: [
        # eth and eth-like
        weth.address,
        # btc and btc-like
        wbtc.address,
    ]
}.get(chain.id, [])

async def _sense_check(
    token_address: str, 
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

    print('this prints')
    # proceed with sense check
    price_readable = round(price, 4)
    symbol = await ERC20(token_address).symbol_async
    network = Network.name(chain.id)
    logger.warning(f'unusually high price (${price_readable}) returned for {symbol} {token_address} on {network}. This does not necessarily mean that the price is wrong, but you may want to validate the price for yourself before proceeding.')


@yLazyLogger(logger)
async def _exit_sense_check(token_address: str) -> bool:
    '''
    For some token types, its normal to have a crazy high nominal price.
    We can skip the sense check for those.
    We can also skip wrapped versions of tokens in `ACCEPTABLE_HIGH_PRICES`.
    '''

    bucket = await check_bucket_async(token_address)

    if bucket == 'uni or uni-like lp':
        return True
    
    elif bucket == 'balancer pool':
        return True
    
    # for wrapped tokens, if the base token is in `ACCEPTABLE_HIGH_PRICES` we can exit the sense check

    elif bucket == 'yearn or yearn-like':
        try: # v2
            underlying = await raw_call_async(token_address, 'token()', output='address')
            if underlying in ACCEPTABLE_HIGH_PRICES or await _exit_sense_check(underlying):
                return True
        except:
            pass
        try: # v1
            underlying = await raw_call_async(token_address, 'want()', output='address')
            if underlying in ACCEPTABLE_HIGH_PRICES or await _exit_sense_check(underlying):
                return True
        except:
            pass
    
    elif bucket == 'atoken':
        try: # v2
            underlying = await raw_call_async(token_address, 'UNDERLYING_ASSET_ADDRESS()', output='address')
            if underlying in ACCEPTABLE_HIGH_PRICES or await _exit_sense_check(underlying):
                return True
        except:
            pass
        try: # v1
            underlying = await raw_call_async(token_address, 'underlyingAssetAddress()', output='address')
            if underlying in ACCEPTABLE_HIGH_PRICES or await _exit_sense_check(underlying):
                return True
        except:
            pass

    elif bucket == 'compound':
        underlying = await raw_call_async(token_address, 'underlying()', output='address')
        if underlying in ACCEPTABLE_HIGH_PRICES or await _exit_sense_check(underlying):
            return True
    
    return False
