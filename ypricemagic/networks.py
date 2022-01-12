
from enum import IntEnum


class Network(IntEnum):
    Mainnet = 1
    BinanceSmartChain = 56
    Polygon = 137
    Fantom = 250
    Arbitrum = 42161
    Avalanche = 43114

    @staticmethod
    def label(chain_id):
        if chain_id == Network.Mainnet:                 return 'ETH'
        elif chain_id == Network.BinanceSmartChain:     return 'BSC'
        elif chain_id == Network.Fantom:                return 'FTM'
        elif chain_id == Network.Polygon:               return 'POLY'
        elif chain_id == Network.Arbitrum:              return 'ARRB'
        elif chain_id == Network.Avalanche:             return 'AVAX'
    
    @staticmethod
    def name(chain_id):
        if chain_id == Network.Mainnet:                 return 'Mainnet'
        elif chain_id == Network.BinanceSmartChain:     return 'Binance Smart Chain'
        elif chain_id == Network.Fantom:                return 'Fantom'
        elif chain_id == Network.Polygon:               return 'Polygon'
        elif chain_id == Network.Arbitrum:              return 'Arbitrum'
        elif chain_id == Network.Avalanche:             return 'Avalanche'
