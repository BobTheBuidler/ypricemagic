
from functools import lru_cache

from brownie import chain
from y.contracts import Contract
from y.exceptions import NotAUniswapV2Pool, call_reverted
from y.networks import Network
from ypricemagic.utils.multicall import fetch_multicall
from ypricemagic.utils.raw_calls import _decimals, raw_call


@lru_cache(maxsize=None)
class UniswapPoolV2:
    def __init__(self, pool_address: str) -> None:
        self.address = pool_address
        self.decimals = _decimals(self.address, return_None_on_failure=True)
        if self.decimals is None: raise NotAUniswapV2Pool
        self.scale = 10 ** self.decimals
        try: self.factory = raw_call(self.address, 'factory()', output='address')
        except ValueError as e:
            if call_reverted(e): raise NotAUniswapV2Pool
            # `is not a valid ETH address` means we got some kind of response from the chain.
            # but couldn't convert to address. If there happens to be a goofy but
            # verified uni fork, maybe we can get factory this way
            okay_errors = ['is not a valid ETH address','invalid opcode','invalid jump destination']
            if any([msg in str(e) for msg in okay_errors]):
                try: self.factory = Contract(self.address).factory()
                except AttributeError: raise NotAUniswapV2Pool
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


    
    