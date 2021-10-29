from brownie import Contract, chain
from cachetools.func import ttl_cache
from .utils.multicall2 import fetch_multicall
from .utils.cache import memory


@ttl_cache(ttl=600)
def get_markets():
    if chain.id == 1: # eth mainnet
        comptroller = Contract("0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B")
        creamtroller = Contract('0x3d5BC3c8d13dcB8bF317092d84783c2697AE9258')
        ironbankroller = Contract("0xAB1c342C7bf5Ec5F02ADEA1c2270670bCa144CbB")
        
        results = fetch_multicall(
            [comptroller, 'getAllMarkets'],
            [creamtroller, 'getAllMarkets'],
            [ironbankroller, 'getAllMarkets'],
        )
        names = ['compound', 'cream', 'ironbank']
        return dict(zip(names, results))
    elif chain.id == 56: # bsc mainnet
        venustroller = Contract("0xfD36E2c2a6789Db23113685031d7F16329158384")
        results = [venustroller.getAllMarkets()]
        names = ['venus']
        return dict(zip(names, results))
    elif chain.id == 137: # poly mainnet
        easytroller = Contract("0xcb3fA413B23b12E402Cfcd8FA120f983FB70d8E8")
        try:
            results = [easytroller.getAllMarkets()]
        except:
            from .interfaces.compound.unitroller  import UNITROLLER_ABI
            easytroller = Contract.from_abi('Unitroller',"0xcb3fA413B23b12E402Cfcd8FA120f983FB70d8E8", UNITROLLER_ABI)
            results = [easytroller.getAllMarkets()]
        names = ['easyfi']
        return dict(zip(names, results))


@memory.cache()
def is_compound_market(token):
    markets = get_markets()
    if any(token in market for market in markets.values()):
        return True
    # NOTE: Workaround for pools that have since been revoked
    token_contract = Contract(token)
    required = {"isCToken", "comptroller", "underlying"} 
    return set(token_contract.__dict__) & required == required


def get_price(token, block=None):
    token = Contract(token)
    if chain.id in [1]:
        try:
            underlying, exchange_rate, decimals = fetch_multicall(
                [token, 'underlying'],
                [token, 'exchangeRateCurrent'],
                [token, 'decimals'],
                block=block
            )
            exchange_rate /= 1e18
            under_decimals = Contract(underlying).decimals()
            return [exchange_rate * 10 ** (decimals - under_decimals), underlying]
        except AttributeError:
            exchange_rate, decimals = fetch_multicall(
                [token, 'exchangeRateCurrent'],
                [token, 'decimals'],
                block=block
            )
            exchange_rate /= 1e18
            under_decimals = 18
            return [exchange_rate * 10 ** (decimals - under_decimals), "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"]
    elif chain.id in [56,137]: # no multicall2 on bsc or poly :(
        try:
            underlying = token.underlying(block_identifier = block)
            exchange_rate = token.exchangeRateStored(block_identifier = block)
            decimals = token.decimals(block_identifier = block)
            exchange_rate /= 1e18
            under_decimals = Contract(underlying).decimals()
            return [exchange_rate * 10 ** (decimals - under_decimals), underlying]
        except AttributeError:
            exchange_rate = token.exchangeRateStored(block_identifier = block)
            decimals = token.decimals(block_identifier = block)
            exchange_rate /= 1e18
            under_decimals = 18
            return [exchange_rate * 10 ** (decimals - under_decimals), "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"]