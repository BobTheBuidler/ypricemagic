
import logging
from typing import Union

from brownie import chain
from y.constants import wbtc, weth
from y.networks import Network
from ypricemagic.utils.raw_calls import _symbol, raw_call

logger = logging.getLogger(__name__)

# This module is far from perfect, but provides an acceptable way to validate some of the prices returned by `get_price`

ACCEPTABLE_HIGH_PRICES = {
    Network.Mainnet: [
        # eth and eth-like
        "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE", # eth
        weth.address,
        "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0", #wsteth
        "0xA3D87FffcE63B53E0d54fAa1cc983B7eB0b74A9c", # ecrv
        "0xaA17A236F2bAdc98DDc0Cf999AbB47D47Fc0A6Cf", # ankrcrv
        "0x53a901d48795C58f485cBB38df08FA96a24669D5", # rcrv
        "0xC4C319E2D4d66CcA4464C0c2B32c9Bd23ebe784e", # alETH+ETH-f
        "0x06325440D014e39736583c165C2963BA99fAf14E", # stecrv
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
        # gold tokens
        "0x4922a015c4407F87432B179bb209e125432E4a2A", # xaut
        # other
        "0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e", # yfi
        "0xD5525D397898e5502075Ea5E830d8914f6F0affe", # meme
        "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2", # mkr
        "0x9cea2eD9e47059260C97d697f82b8A14EfA61EA5", # punk
        "0x69BbE2FA02b4D90A944fF328663667DC32786385", # punk-basic
        "0x23B608675a2B2fB1890d3ABBd85c5775c51691d5", # socks
        "0xcA3d75aC011BF5aD07a98d02f18225F9bD9A6BDF", # crvtricrypto
        "0xc4AD29ba4B3c580e6D59105FFf484999997675Ff", # crv3crypto
        "0xd075e95423C5c4BA1E122CaE0f4CdFA19b82881b", # wPE
        "0xe9F84dE264E91529aF07Fa2C746e934397810334", # sak3
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
    ],
}.get(chain.id, [])

def _sense_check(
    token_address: str, 
    price: float,
    bucket: Union[str, None]
    ):

    # if price is in "normal" range, exit sense check

    if price < 1000:
        return
    
    # if we've already validated that the token should have a high price, exit sense check

    if token_address in ACCEPTABLE_HIGH_PRICES:
        return

    # for some token types, its normal to have a crazy high nominal price
    # we can skip the sense check for those

    if bucket == 'uni or uni-like lp':
        return
    
    elif bucket == 'balancer pool':
        return

    # for wrapped tokens, if the base token is in `ACCEPTABLE_HIGH_PRICES` we can exit the sense check

    elif bucket == 'yearn or yearn-like':
        try: # v2
            token_address = raw_call(token_address, 'token()', output='address')
            if token_address in ACCEPTABLE_HIGH_PRICES: return
        except:
            try: # v1
                token_address = raw_call(token_address, 'want()', output='address')
                if token_address in ACCEPTABLE_HIGH_PRICES: return
            except: pass
    
    elif bucket == 'atoken':
        try: # v2
            token_address = raw_call(token_address, 'UNDERLYING_ASSET_ADDRESS()', output='address')
            if token_address in ACCEPTABLE_HIGH_PRICES: return
        except:
            try: # v1
                token_address = raw_call(token_address, 'underlyingAssetAddress()', output='address')
                if token_address in ACCEPTABLE_HIGH_PRICES: return
            except: pass

    elif bucket == 'compound':
        token_address = raw_call(token_address, 'underlying()', output='address')
        if token_address in ACCEPTABLE_HIGH_PRICES: return

    # proceed with sense check

    price_readable = round(price, 4)
    symbol = _symbol(token_address)
    network = Network.name(chain.id)
    logger.warn(f'unusually high price (${price_readable}) returned for {symbol} {token_address} on {network}. This does not necessarily mean that the price is wrong, but you may want to validate the price for yourself before proceeding.')
