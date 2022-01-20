
from functools import lru_cache

from brownie import chain
from y.contracts import Contract
from y.exceptions import NotUniswapPoolV2
from y.networks import Network
from ypricemagic.utils.multicall import fetch_multicall
from ypricemagic.utils.raw_calls import NonStandardERC20, _decimals, raw_call


@lru_cache(maxsize=None)
class UniswapPoolV2:
    def __init__(self, pool_address: str) -> None:
        self.address = pool_address
        self.decimals = _decimals(self.address, return_None_on_failure=True)
        if self.decimals is None: raise NotUniswapPoolV2
        self.scale = 10 ** self.decimals
        try: self.factory = raw_call(self.address, 'factory()', output='address')
        except ValueError as e:
            if 'execution reverted' in str(e): raise NotUniswapPoolV2
            # `is not a valid ETH address` means we got some kind of response from the chain.
            # but couldn't convert to address. If there happens to be a goofy but
            # verified uni fork, maybe we can get factory this way
            okay_errors = ['is not a valid ETH address','invalid opcode','invalid jump destination']
            if any([msg in str(e) for msg in okay_errors]):
                try: self.factory = Contract(self.address).factory()
                except AttributeError: raise NotUniswapPoolV2
            else: raise

    def get_pool_details(self, block=None):
        pair = Contract(self.address)
        if chain.id in [Network.Mainnet, Network.BinanceSmartChain, Network.Polygon, Network.Fantom]: 
            token0, token1, supply, reserves = fetch_multicall(
                [pair, "token0"],
                [pair, "token1"],
                [pair, "totalSupply"],
                [pair, "getReserves"],
                block=block
            )
        else: # if your chain does not support multicall
            token0 = pair.token0(block_identifier = block)
            token1 = pair.token1(block_identifier = block)
            supply = pair.totalSupply(block_identifier = block)
            reserves = pair.getReserves(block_identifier = block)

        return token0, token1, supply, reserves


    
    