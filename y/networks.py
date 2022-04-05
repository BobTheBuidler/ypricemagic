
from enum import IntEnum
from typing import Optional

from brownie import chain


class Network(IntEnum):
    Mainnet = 1
    BinanceSmartChain = 56
    xDai = 100
    Heco = 128
    Polygon = 137
    Fantom = 250
    Moonriver = 1285
    Arbitrum = 42161
    Avalanche = 43114
    Harmony = 1666600000
    Aurora = 1313161554
    OKEx = 66
    Cronos = 25

    @staticmethod
    def label(chain_id: Optional[int] = None) -> str:
        if not chain_id: chain_id = chain.id

        if chain_id == Network.Mainnet:                 return 'ETH'
        elif chain_id == Network.BinanceSmartChain:     return 'BSC'
        elif chain_id == Network.xDai:                  return 'XDAI'
        elif chain_id == Network.Heco:                  return 'HECO'
        elif chain_id == Network.Polygon:               return 'POLY'
        elif chain_id == Network.Fantom:                return 'FTM'
        elif chain_id == Network.Moonriver:             return 'MOVR'
        elif chain_id == Network.Arbitrum:              return 'ARRB'
        elif chain_id == Network.Avalanche:             return 'AVAX'
        elif chain_id == Network.Harmony:               return 'ONE'
        elif chain_id == Network.Aurora:                return 'AURORA'
        elif chain_id == Network.OKEx:                  return 'OKEX'
        elif chain_id == Network.Cronos:                return 'CRO'
    
    @staticmethod
    def name(chain_id: Optional[int] = None) -> str:
        if not chain_id: chain_id = chain.id

        if chain_id == Network.Mainnet:                 return 'Mainnet'
        elif chain_id == Network.BinanceSmartChain:     return 'Binance Smart Chain'
        elif chain_id == Network.xDai:                  return 'xDai'
        elif chain_id == Network.Heco:                  return 'Heco'
        elif chain_id == Network.Polygon:               return 'Polygon'
        elif chain_id == Network.Fantom:                return 'Fantom'
        elif chain_id == Network.Moonriver:             return 'Moonriver'
        elif chain_id == Network.Arbitrum:              return 'Arbitrum'
        elif chain_id == Network.Avalanche:             return 'Avalanche'
        elif chain_id == Network.Harmony:               return "HarmonyOne Shard 0"
        elif chain_id == Network.Aurora:                return 'Aurora'
        elif chain_id == Network.OKEx:                  return 'OKEx'
        elif chain_id == Network.Cronos:                return 'Cronos'

    @staticmethod
    def printable(chain_id: Optional[int] = None) -> str:
        # will always work to print a readable string that identifies the network, even if network not supported
        if chain_id is None: chain_id = chain.id
        return Network.name(chain_id) if Network.name(chain_id) else f"chain {chain_id}"
