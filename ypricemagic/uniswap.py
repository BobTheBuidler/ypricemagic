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
    
# NOTE: If this is failing to pull a price for a token you need, it's likely because that token requires a special swap path.
#       Please add a viable swap path below to fetch price data successfully.

#project.load()

if chain.id == 1:
    FACTORIES = {
        "uniswap": "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",
        "sushiswap": "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac",
        "shibaswap": "0x115934131916C8b277DD010Ee02de363c09d037c",
    }
    ROUTERS = {
        "uniswap": Contract("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"),
        "sushiswap": Contract("0xD9E1CE17F2641F24AE83637AB66A2CCA9C378B9F"),
        "shibaswap": Contract("0x03f7724180AA6b939894B5Ca4314783B0b36b329"),
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
            ,"0x62B9c7356A2Dc64a1969e19C23e4f579F9810Aa7": ["0x62B9c7356A2Dc64a1969e19C23e4f579F9810Aa7","0xD533a949740bb3306d119CC777fa900bA034cd52",weth,usdc]
        },
        "uniswap": {

        },
        "shibaswap": {

        }
    }
elif chain.id == 56:
    ROUTERS = {
        "pancakeswapv2": Contract("0x10ED43C718714eb63d5aA57B78B54704E256024E"),
        "pancakeswapv1": Contract("0x05fF2B0DB69458A0750badebc4f9e13aDd608C7F"),
        "wault": Contract("0xD48745E39BbED146eEC15b79cBF964884F9877c2"),
        "apeswap": Contract('0xcF0feBd3f17CEf5b47b0cD257aCf6025c5BFf3b7'),
        "swapliquidity": Contract('0x70e139f4C3C4A58b2D586490aB608eAf3c1F0995'),
    }
    FACTORIES = {
        "pancakeswapv2": "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73",
        "pancakeswapv1": "0xBCfCcbde45cE874adCB698cC183deBcF17952812",
        "wault": "0xB42E3FE71b7E0673335b3331B3e1053BD9822570",
        "apeswap": "0x0841BD0B734E4F5853f0dD8d7Ea041c241fb0Da6",
        "swapliquidity": "0x553990F2CBA90272390f62C5BDb1681fFc899675",
    }
    SPECIAL_PATHS = {
        "pancakeswapv2": {

        },
        "pancakeswapv1": {

        },
        "wault": {

        },
        "apeswap": {

        },
        "swapliquidity": {

        },
    }
elif chain.id == 137:
    ROUTERS = {
        "quickswap": Contract("0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff"),
        "sushi": Contract("0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"),
        "dfyn": Contract("0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff"),
        "wault": Contract("0x3a1D87f206D12415f5b0A33E786967680AAb4f6d"),
        "cometh": Contract.from_abi("ComethSwapRouter","0x28E73C83C0f85784543300B96A1A3c2e900F7a35",Contract("0x3a1D87f206D12415f5b0A33E786967680AAb4f6d").abi)
    }
    FACTORIES = {
        "quickswap": "0x5757371414417b8C6CAad45bAeF941aBc7d3Ab32",
        "sushi": "0xc35DADB65012eC5796536bD9864eD8773aBc74C4",
        "dfyn": "0x5757371414417b8C6CAad45bAeF941aBc7d3Ab32",
        "wault": "0xa98ea6356A316b44Bf710D5f9b6b4eA0081409Ef",
        "cometh": "0x800b052609c355cA8103E06F022aA30647eAd60a",
    }
    SPECIAL_PATHS = {
        "quickswap": {

        },
        "sushi": {

        },
        "dfyn": {

        },
        "wault": {

        },
        "cometh": {

        },
    }
elif chain.id == 250:
    ROUTERS = {
        'sushi': Contract('0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506'),
        'spookyswap': Contract('0xF491e7B69E4244ad4002BC14e878a34207E38c29'),
        'spiritswap': Contract('0x16327E3FbDaCA3bcF7E38F5Af2599D2DDc33aE52')
    }
    FACTORIES = {
        "sushi": "0xc35DADB65012eC5796536bD9864eD8773aBc74C4",
        "spookyswap": "0x152eE697f2E276fA89E96742e9bB9aB1F2E61bE3",
        "spiritswap": "0xEF45d134b73241eDa7703fa787148D9C9F4950b0",
    }
    SPECIAL_PATHS = {
        "sushi": {

        },
        "spookyswap": {

        },
        "spiritswap": {

        }
    }

FACTORY_TO_ROUTER = {FACTORIES[name]: ROUTERS[name] for name in FACTORIES}

FACTORY_TO_PROTOCOL = {FACTORIES[name]: name for name in FACTORIES}


@ttl_cache(ttl=36000)
def get_price(token_in, token_out=usdc, router="uniswap", block=None, paired_against=weth):
    """
    Calculate a price based on Uniswap Router quote for selling one `token_in`.
    Always uses intermediate WETH pair if `[token_in,weth,token_out]` swap path available.
    """
    if chain.id == 56 and token_out == usdc:
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
        from .constants import cake, wbnb
        if wbnb in (token_in, token_out):
            path = [token_in, token_out]
        elif cake in (token_in, token_out):
            path = [token_in, token_out]
        else:
            path = [token_in,wbnb,token_out]
    elif chain.id == 137: # polygon
        from .constants import wmatic
        if wmatic in (token_in, token_out):
            path = [token_in, token_out]
        else:
            path = [token_in,wmatic,token_out]
    elif chain.id == 250: # fantom
        from .constants import wftm
        if wftm in (token_in, token_out):
            path = [token_in, token_out]
        else:
            path = [token_in, wftm, token_out]
    else:
        path = [token_in, weth, token_out]
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
    if chain.id not in [56, 137]: # No multicall2 on bsc or poly
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