

from brownie import chain
from cachetools.func import ttl_cache
from ypricemagic.constants import usdc, weth, sushi
from ypricemagic.price_modules.uniswap.protocols import ROUTER_TO_FACTORY, special_paths
from ypricemagic.networks import Network
from ypricemagic.utils.contracts import Contract
from ypricemagic.constants import STABLECOINS
from ypricemagic.utils.raw_calls import _decimals

class UniswapRouterV2:
    def __init__(self, router_address) -> None:
        self.address = router_address
        self.contract = Contract(self.address)
        self.factory = ROUTER_TO_FACTORY[self.address]
        self.special_paths = special_paths(self.address)

    @ttl_cache(ttl=36000)
    def get_price(self, token_in, token_out=usdc, block=None, paired_against=weth):
        """
        Calculate a price based on Uniswap Router quote for selling one `token_in`.
        Always uses intermediate WETH pair if `[token_in,weth,token_out]` swap path available.
        """

        token_in, token_out = str(token_in), str(token_out)

        if chain.id == Network.BinanceSmartChain and token_out == usdc:
            busd = Contract("0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56")
            token_out = busd

        amount_in = 10 ** _decimals(token_in,block)

        if str(token_in) in STABLECOINS: return 1

        path = self.path_selector(token_in, token_out, paired_against)
        fees = 0.997 ** (len(path) - 1)
        quote = self.contract.getAmountsOut(amount_in, path, block_identifier=block)
        amount_out = quote[-1] / 10 ** _decimals(str(path[-1]),block)
        return amount_out / fees

    def path_selector(self, token_in, token_out, paired_against):

        if str(paired_against) in STABLECOINS and str(token_out) in STABLECOINS:            path = [token_in, paired_against]
        elif weth in (token_in, token_out):                                                 path = [token_in, token_out]
        elif paired_against == sushi and token_out != sushi:                                path = [token_in,sushi,weth,token_out]
        elif str(token_in) in self.special_paths and str(token_out) in STABLECOINS:  path = self.special_paths[str(token_in)]

        elif chain.id == Network.BinanceSmartChain:
            from ypricemagic.constants import cake, wbnb
            if wbnb in (token_in, token_out):                                               path = [token_in, token_out]
            elif cake in (token_in, token_out):                                             path = [token_in, token_out]
            else:                                                                           path = [token_in,wbnb,token_out]
        elif chain.id == Network.Polygon:
            from ypricemagic.constants import wmatic
            if wmatic in (token_in, token_out):                                             path = [token_in, token_out]
            else:                                                                           path = [token_in,wmatic,token_out]
        elif chain.id == Network.Fantom:
            from ypricemagic.constants import wftm
            if wftm in (token_in, token_out):                                               path = [token_in, token_out]
            else:                                                                           path = [token_in, wftm, token_out]

        else:                                                                               path = [token_in, weth, token_out]

        return path
    