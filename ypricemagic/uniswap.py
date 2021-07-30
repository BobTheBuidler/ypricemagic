import token
from tokenize import tokenize
from brownie import Contract, chain
from brownie.exceptions import ContractNotFound
from cachetools.func import ttl_cache
from .utils.cache import memory
from .utils.multicall2 import fetch_multicall
from .interfaces.ERC20 import ERC20ABI
import ypricemagic.magic
import ypricemagic.utils.utils
from .constants import STABLECOINS, dai, usdc, usdt, wbtc, weth, sushi
    


#project.load()

if chain.id == 1:
    FACTORIES = {
        "uniswap": "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",
        "sushiswap": "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac",
    }
    ROUTERS = {
        "uniswap": Contract("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"),
        "sushiswap": Contract("0xD9E1CE17F2641F24AE83637AB66A2CCA9C378B9F"),
    }
    SPECIAL_PATHS = {
        "sushiswap": {
            "0xEF69B5697f2Fb0345cC680210fD39b593a2f9684": ["0xEF69B5697f2Fb0345cC680210fD39b593a2f9684","0x6B3595068778DD592e39A122f4f5a5cF09C90fE2",weth,usdc]
            ,"0xbf2179859fc6D5BEE9Bf9158632Dc51678a4100e": ["0xbf2179859fc6D5BEE9Bf9158632Dc51678a4100e","0xC28E27870558cF22ADD83540d2126da2e4b464c2",weth,usdc]
            ,"0x3166C570935a7D8554c8f4eA792ff965D2EFe1f2": ["0x3166C570935a7D8554c8f4eA792ff965D2EFe1f2","0x4954Db6391F4feB5468b6B943D4935353596aEC9",usdc]
            ,"0xE6279E1c65DD41b30bA3760DCaC3CD8bbb4420D6": ["0xE6279E1c65DD41b30bA3760DCaC3CD8bbb4420D6","0x87F5F9eBE40786D49D35E1B5997b07cCAA8ADbFF",weth,usdc]
            ,"0x4954Db6391F4feB5468b6B943D4935353596aEC9": ["0x4954Db6391F4feB5468b6B943D4935353596aEC9",usdc]
            ,"0x1E18821E69B9FAA8e6e75DFFe54E7E25754beDa0": ["0x1E18821E69B9FAA8e6e75DFFe54E7E25754beDa0","0xEF69B5697f2Fb0345cC680210fD39b593a2f9684","0x6B3595068778DD592e39A122f4f5a5cF09C90fE2",weth,usdc]
            ,"0xfC1E690f61EFd961294b3e1Ce3313fBD8aa4f85d": ["0xfC1E690f61EFd961294b3e1Ce3313fBD8aa4f85d","0xba100000625a3754423978a60c9317c58a424e3D",weth,usdc]
            ,"0xBA50933C268F567BDC86E1aC131BE072C6B0b71a": ["0xBA50933C268F567BDC86E1aC131BE072C6B0b71a",weth,usdc]
            ,"0x6102407f07029892eB5Ff02164ADFaFb85f4d222": ["0x6102407f07029892eB5Ff02164ADFaFb85f4d222",usdt]
            ,"0x85034b3b2e292493D029443455Cc62ab669573B3": ["0x85034b3b2e292493D029443455Cc62ab669573B3","0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",weth,usdc]
            ,"0xb220D53F7D0f52897Bcf25E47c4c3DC0bac344F8": ["0xb220D53F7D0f52897Bcf25E47c4c3DC0bac344F8", usdc]
            ,"0x383518188C0C6d7730D91b2c03a03C837814a899": ["0x383518188C0C6d7730D91b2c03a03C837814a899",dai]
            ,"0xafcE9B78D409bF74980CACF610AFB851BF02F257": ["0xafcE9B78D409bF74980CACF610AFB851BF02F257",wbtc,weth,usdc]
        },
        "uniswap": {

        }
    }
elif chain.id == 56:
    ROUTERS = {
        "pancakeswap": Contract("0x10ED43C718714eb63d5aA57B78B54704E256024E"),
    }
    FACTORIES = {
        "pancakeswap": "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73",
    }
    SPECIAL_PATHS = {
        "pancakeswap": {

        }
    }

FACTORY_TO_ROUTER = {FACTORIES[name]: ROUTERS[name] for name in FACTORIES}

FACTORY_TO_PROTOCOL = {FACTORIES[name]: name for name in FACTORIES}


@ttl_cache(ttl=600)
def get_price(token_in, token_out=usdc, router="uniswap", block=None, paired_against=weth):
    """
    Calculate a price based on Uniswap Router quote for selling one `token_in`.
    Always uses intermediate WETH pair if `[token_in,weth,token_out]` swap path available.
    """
    if chain.id == 56:
        busd = Contract("0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56")
        token_out = busd
    tokens = [str(token) for token in [token_in, token_out]]
    amount_in = 10 ** ypricemagic.utils.utils.get_decimals_with_override(tokens[0])
    
    if str(token_in) in STABLECOINS:
        return 1
    elif str(paired_against) in STABLECOINS and str(token_out) in STABLECOINS:
        path = [token_in, paired_against]
    elif weth in (token_in, token_out):
        path = [token_in, token_out]
    elif paired_against == sushi and token_out != sushi:
        path = [token_in,sushi,weth,token_out]
    elif str(token_in) in SPECIAL_PATHS[router].keys() and str(token_out) in STABLECOINS:
        path = SPECIAL_PATHS[router][str(token_in)]
    elif chain.id == 56: #bsc
        wbnb = Contract("0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c")
        cake = Contract("0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82")
        if wbnb in (token_in, token_out):
            path = [token_in, token_out]
        elif cake in (token_in, token_out):
            path = [token_in, token_out]
        else:
            path = [token_in,wbnb,token_out]
    else:
        path = [token_in, weth, token_out]
    #print(path)
    fees = 0.997 ** (len(path) - 1)
    if router in ROUTERS:
        router = ROUTERS[router]
    try:
        quote = router.getAmountsOut(amount_in, path, block_identifier=block)
        amount_out = quote[-1] / 10 ** ypricemagic.utils.utils.get_decimals_with_override(str(path[-1]))
        return amount_out / fees
    except ValueError as e:
        return


@ttl_cache(ttl=600)
def get_price_v1(asset, block=None):
    factory = Contract("0xc0a47dFe034B400B47bDaD5FecDa2621de6c4d95")
    try:
        exchange = Contract(factory.getExchange(asset))
        eth_bought = exchange.getTokenToEthInputPrice(10 ** ypricemagic.utils.utils.get_decimals_with_override(asset), block_identifier=block)
        exchange = Contract(factory.getExchange(usdc))
        usdc_bought = exchange.getEthToTokenInputPrice(eth_bought, block_identifier=block) / 1e6
        fees = 0.997 ** 2
        return usdc_bought / fees
    except (ContractNotFound, ValueError) as e:
        pass


@memory.cache()
def is_uniswap_pool(address):
    try:
        return Contract(address).factory() in FACTORY_TO_ROUTER
    except (ValueError, OverflowError, AttributeError):
        pass
    return False


@ttl_cache(ttl=600)
def lp_price(address, block=None):
    """ Get Uniswap/Sushiswap LP token price. """

    def extrapolate_balance_if_needed():
        nonlocal balances
        if balances[0] and not balances[1]:
            balances[1] = balances[0]
        if balances[1] and not balances[0]:
            balances[0] = balances[1]
        return balances

    pair = Contract(address)
    if chain.id not in [56]: # No multicall2 on bsc
        factory, token0, token1, supply, reserves = fetch_multicall(
            [pair, "factory"],
            [pair, "token0"],
            [pair, "token1"],
            [pair, "totalSupply"],
            [pair, "getReserves"],
            block=block
        )
    else:
        factory = pair.factory(block_identifier = block)
        token0 = pair.token0(block_identifier = block)
        token1 = pair.token1(block_identifier = block)
        supply = pair.totalSupply(block_identifier = block)
        reserves = pair.getReserves(block_identifier = block)
    router = FACTORY_TO_PROTOCOL[factory]
    tokens = [ypricemagic.utils.utils.Contract_with_erc20_fallback(token) for token in [token0, token1]]
    price0 = get_price(tokens[0], paired_against=tokens[1], router=router, block=block)
    price1 = get_price(tokens[1], paired_against=tokens[0], router=router, block=block)
    print(tokens)
    print(reserves)
    prices = [price0,price1]
    scales = [10 ** ypricemagic.utils.utils.get_decimals_with_override(str(token)) for token in tokens]
    supply = supply / 1e18
    try:
        balances = [res / scale * price for res, scale, price in zip(reserves, scales, prices)]
    except TypeError as e: # If can't get price via router, try to get from elsewhere
        if not price0:
            try:
                price0 = ypricemagic.magic.get_price(tokens[0], block)
            except ypricemagic.magic.PriceError:
                price0 is None
        if not price1:
            try:
                price1 = ypricemagic.magic.get_price(tokens[1], block)
            except ypricemagic.magic.PriceError:
                price1 is None
        prices = [price0,price1]
        balances = [None,None] # [res / scale * price for res, scale, price in zip(reserves, scales, prices)]
        if price0:
            balances[0] = reserves[0] / scales[0] * price0
        if price1:
            balances[1] = reserves[1] / scales[1] * price1
    balances = extrapolate_balance_if_needed()
    try:
        return sum(balances) / supply
    except TypeError:
        return