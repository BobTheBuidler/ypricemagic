
from brownie import chain
from ypricemagic.networks import Network
from ypricemagic.utils.contracts import Contract
from ypricemagic.utils.raw_calls import raw_call, _decimals
from ypricemagic.utils.multicall import fetch_multicall


class NotUniswapPoolV2(Exception):
    pass


class UniswapPoolV2:
    def __init__(self, pool_address: str) -> None:
        self.address = pool_address
        self.decimals = _decimals(self.address)
        self.scale = 10 ** self.decimals
        try: self.factory = raw_call(pool_address, 'factory()', output='address')
        except ValueError as e:
            if 'execution reverted' in str(e): raise NotUniswapPoolV2
            else: raise

    def get_pool_details(self, block=None):
        pair = Contract(self.address)
        factory = self.factory
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

        return {
            "factory": factory,
            'token0': token0,
            'token1': token1,
            'supply': supply,
            'reserves': reserves,
        }


    
    