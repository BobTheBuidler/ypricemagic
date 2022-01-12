
from enum import IntEnum


class Network(IntEnum):
    Mainnet = 1
    BinanceSmartChain = 56
    Fantom = 250
    Polygon = 137
    Arbitrum = 42161
    Avalanche = 43114

    @staticmethod
    def label(chain_id):
        if chain_id == Network.Mainnet:                 return 'ETH'
        elif chain_id == Network.BinanceSmartChain:     return 'BSC'
        elif chain_id == Network.Fantom:                return "FTM"
        elif chain_id == Network.Arbitrum:              return "ARRB"
