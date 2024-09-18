
from enum import IntEnum
from typing import Optional

from brownie import chain


class Network(IntEnum):
    """
    A lightweight enum that enables lookup of chainids for popular blockchain networks.

    Each network is associated with its unique integer Chain ID.
    """

    # NOTE: If a particular network has changed names, do not remove
    # the old spec, simply add the new spec directly above the old one.
    # Both will work but Network(chainid) will return the new name. """

    Mainnet = 1
    """The Chain ID for Ethereum Mainnet"""

    Optimism = 10
    """The Chain ID for Optimism"""

    Cronos = 25
    """The Chain ID for Cronos Mainnet"""

    BinanceSmartChain = 56
    """The Chain ID for Binance Smart Chain"""

    OKEx = 66
    """The Chain ID for OKEx Chain"""

    Gnosis = 100
    """The Chain ID for xDai Chain (now Gnosis Chain)"""

    xDai = 100
    """The Chain ID for xDai Chain (now Gnosis Chain)"""

    Heco = 128
    """The Chain ID for Heco"""

    Polygon = 137
    """The Chain ID for Polygon (formerly Matic) Network"""

    Fantom = 250
    """The Chain ID for Fantom Opera Network"""

    Moonriver = 1285
    """The Chain ID for Moonriver Network"""

    Base = 8453
    """The Chain ID for Base"""

    Arbitrum = 42161
    """The Chain ID for Arbitrum One"""

    Avalanche = 43114
    """The Chain ID for Avalanche C-Chain"""

    Harmony = 1666600000
    """The Chain ID for Harmony Mainnet Shard 0"""

    Aurora = 1313161554
    """The Chain ID for Aurora"""

    @staticmethod
    def label(chain_id: Optional[int] = None) -> str:
        if not chain_id: chain_id = chain.id

        if chain_id == Network.Mainnet:                 return 'ETH'
        elif chain_id == Network.BinanceSmartChain:     return 'BSC'
        elif chain_id == Network.Gnosis:                return 'GNO'
        elif chain_id == Network.Heco:                  return 'HECO'
        elif chain_id == Network.Polygon:               return 'POLY'
        elif chain_id == Network.Fantom:                return 'FTM'
        elif chain_id == Network.Moonriver:             return 'MOVR'
        elif chain_id == Network.Arbitrum:              return 'ARB'
        elif chain_id == Network.Avalanche:             return 'AVAX'
        elif chain_id == Network.Harmony:               return 'ONE'
        elif chain_id == Network.Aurora:                return 'AURORA'
        elif chain_id == Network.OKEx:                  return 'OKEX'
        elif chain_id == Network.Cronos:                return 'CRO'
        elif chain_id == Network.Optimism:              return 'OPTI'
        elif chain_id == Network.Base:                  return 'BASE'
    
    @staticmethod
    def name(chain_id: Optional[int] = None) -> str:
        if not chain_id: chain_id = chain.id

        if chain_id == Network.Mainnet:                 return 'Mainnet'
        elif chain_id == Network.BinanceSmartChain:     return 'Binance Smart Chain'
        elif chain_id == Network.Gnosis:                return 'Gnosis'
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
        elif chain_id == Network.Optimism:              return "Optimism"
        elif chain_id == Network.Base:                  return "Base"

    @staticmethod
    def printable(chain_id: Optional[int] = None) -> str:
        # will always work to print a readable string that identifies the network, even if network not supported
        if chain_id is None: chain_id = chain.id
        return Network.name(chain_id) or f"chain {chain_id}"
