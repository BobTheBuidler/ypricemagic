from brownie import ZERO_ADDRESS, Contract, chain
from cachetools.func import ttl_cache
from toolz import take

from . import magic

from .constants import dai
from .utils.cache import memory
from .utils.multicall2 import fetch_multicall

# curve registry documentation https://curve.readthedocs.io/registry-address-provider.html
try: # if curve registry not deployed on a chain, skip this stuff
    address_provider = Contract('0x0000000022D53366457F9d5E68Ec105046FC4383')
    curve_registry = Contract(address_provider.get_address(0))
    metapool_factory = None if address_provider.get_address(3) == ZERO_ADDRESS else Contract(address_provider.get_address(3))
except:
    pass

# fold underlying tokens into one of the basic tokens

if chain.id == 1:
    BASIC_TOKENS = {
        dai.address,  # dai
        "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # weth
        "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",  # eth
        "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",  # wbtc
        "0xD71eCFF9342A5Ced620049e616c5035F1dB98620",  # seur
        "0x514910771AF9Ca656af840dff83E8264EcF986CA",  # link
    }
    OVERRIDES = {
        '0x53a901d48795C58f485cBB38df08FA96a24669D5': {
            'name': 'reth',
            'pool': '0xF9440930043eb3997fc70e1339dBb11F341de7A8',
            'coins': [
                '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',  # ETH
                '0x9559Aaa82d9649C7A7b220E7c461d2E74c9a3593',  # rETH
            ],
        }
    }
    CRYPTOPOOLS = {
        '0xcA3d75aC011BF5aD07a98d02f18225F9bD9A6BDF': {
            'pool': '0x80466c64868E1ab14a1Ddf27A676C3fcBE638Fe5',
        }, #TriCrypto
        '0xc4AD29ba4B3c580e6D59105FFf484999997675Ff': {
            'pool': '0xD51a44d3FaE010294C616388b506AcdA1bfAAE46',
        }, # 3Crypto
    }
elif chain.id == 137:
    BASIC_TOKENS = {
        dai.address, 
    }
    OVERRIDES = {}
    '''
    OVERRIDES = {
        '0x53a901d48795C58f485cBB38df08FA96a24669D5': {
            'name': 'reth',
            'pool': '0xF9440930043eb3997fc70e1339dBb11F341de7A8',
            'coins': [
                '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',  # ETH
                '0x9559Aaa82d9649C7A7b220E7c461d2E74c9a3593',  # rETH
            ],
        }
    }
    '''
    CRYPTOPOOLS = {
        '0x8096ac61db23291252574D49f036f0f9ed8ab390': {
            'pool': '0x751B1e21756bDbc307CBcC5085c042a0e9AaEf36',
        }, # tricrypto
        '0xbece5d20A8a104c54183CC316C8286E3F00ffC71': {
            'pool': '0x92577943c7aC4accb35288aB2CC84D75feC330aF',
        }, # tricrypto2
        '0xdAD97F7713Ae9437fa9249920eC8507e5FbB23d3': {
            'pool': '0x92215849c439E1f8612b6646060B4E3E5ef822cC',
        }, # tricrypto3
        '0x600743B1d8A96438bD46836fD34977a00293f6Aa': {
            'pool': '0xB446BF7b8D6D4276d0c75eC0e3ee8dD7Fe15783A',
        }, # 
    }
elif chain.id == 250:
    BASIC_TOKENS = {
        dai.address, 
    }
    OVERRIDES = {}
    '''
    OVERRIDES = {
        '0x53a901d48795C58f485cBB38df08FA96a24669D5': {
            'name': 'reth',
            'pool': '0xF9440930043eb3997fc70e1339dBb11F341de7A8',
            'coins': [
                '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',  # ETH
                '0x9559Aaa82d9649C7A7b220E7c461d2E74c9a3593',  # rETH
            ],
        }
    }
    '''
    CRYPTOPOOLS = {
        '0x58e57cA18B7A47112b877E31929798Cd3D703b0f': {
            'pool': '0x3a1659Ddcf2339Be3aeA159cA010979FB49155FF',
        },
    }




@memory.cache()
def get_pool(token):
    if token in OVERRIDES:
        return OVERRIDES[token]['pool']
    if token in CRYPTOPOOLS:
        return CRYPTOPOOLS[token]['pool']
    try:
        if set(metapool_factory.get_underlying_coins(token)) != {ZERO_ADDRESS}:
            return token
    except:
        try:
            if set(metapool_factory.get_coins(token)) != {ZERO_ADDRESS}:
                return token
        except:
            pass
    return curve_registry.get_pool_from_lp_token(token)


@memory.cache()
def is_curve_lp_token(token):
    return get_pool(token) != ZERO_ADDRESS


@memory.cache()
def get_underlying_coins(token):
    if token in OVERRIDES:
        return OVERRIDES[token]['coins']
    pool = get_pool(token)
    coins = curve_registry.get_underlying_coins(pool)
    if set(coins) == {ZERO_ADDRESS}:
        try:
            coins = metapool_factory.get_underlying_coins(token)
        except ValueError:
            coins = metapool_factory.get_coins(token)
    return [coin for coin in coins if coin != ZERO_ADDRESS]


def cryptopool_lp_price(token, block=None):
    pool = Contract(CRYPTOPOOLS[token]['pool'])
    token = Contract(token)
    result = fetch_multicall(*[[pool, 'coins', i] for i in range(8)])
    tokens = [Contract(token) for token in result if token]
    n = len(tokens)
    try:
        result = iter(
            fetch_multicall(
                [token, 'totalSupply'],
                *[[token, 'decimals'] for token in tokens],
                *[[pool, 'balances', i] for i in range(n)],
                *[[pool, 'price_oracle', i] for i in range(n - 1)],
                block=block
            )
        )
        supply = next(result) / 1e18
        scales = [10 ** decimals for decimals in take(n, result)]
        balances = [balance / scale for balance, scale in zip(take(n, result), scales)]
        # oracles return price with the first coin as a quote currency
        prices = [1] + [price / 1e18 for price in take(n - 1, result)]
        scale = sum(balance * price for balance, price in zip(balances, prices)) / supply
        return [scale, str(tokens[0])]
    # testing
    except TypeError as e:
        if str(e) == "price_oracle requires no arguments":
            result = iter(
                fetch_multicall(
                    [token, 'totalSupply'],
                    *[[token, 'decimals'] for token in tokens],
                    *[[pool, 'balances', i] for i in range(n)],
                    block=block
                )
            )
            supply = next(result) / 1e18
            scales = [10 ** decimals for decimals in take(n, result)]
            balances = [balance / scale for balance, scale in zip(take(n, result), scales)]
            prices = [magic.get_price(token, block) for token in tokens]
            scale = sum(balance * price for balance, price in zip(balances, prices)) / supply
            return [scale, str(tokens[0])]
    

@ttl_cache(ttl=600)
def get_pool_price(token, block=None):
    if token in CRYPTOPOOLS:
        return cryptopool_lp_price(token, block)

    coins = get_underlying_coins(token)
    try:
        coin = (set(coins) & BASIC_TOKENS).pop()
    except KeyError:
        coin = coins[0]

    # there is a registry.get_virtual_price_from_lp_token,
    # but we call pool in case the registry was not deployed at the block
    pool = Contract(get_pool(token))
    try:
        virtual_price = pool.get_virtual_price(block_identifier=block) / 1e18
    except:
        pool = Contract.from_explorer(get_pool(token))
        virtual_price = pool.get_virtual_price(block_identifier=block) / 1e18
    return [virtual_price, coin]
