from enum import IntEnum
from typing import Optional

from brownie import chain


_CHAINID = chain.id


class Network(IntEnum):
    """
    A lightweight enum that enables lookup of chain IDs for popular blockchain networks.

    Each network is associated with its unique integer Chain ID.

    Examples:
        >>> Network.Mainnet
        <Network.Mainnet: 1>
        >>> Network.Mainnet.value
        1
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
        """
        Get the label (abbreviation) for a given chain ID.

        If no chain ID is provided, it defaults to the current active chain.

        Args:
            chain_id: The chain ID of the network.

        Examples:
            >>> Network.label(Network.Mainnet)
            'ETH'
            >>> Network.label()
            'ETH'  # Assuming the current active chain is Mainnet

        See Also:
            :meth:`Network.name` for getting the full name of the network.
        """
        if not chain_id:
            chain_id = _CHAINID

        if chain_id == Network.Mainnet:
            return "ETH"
        elif chain_id == Network.BinanceSmartChain:
            return "BSC"
        elif chain_id == Network.Gnosis:
            return "GNO"
        elif chain_id == Network.Heco:
            return "HECO"
        elif chain_id == Network.Polygon:
            return "POLY"
        elif chain_id == Network.Fantom:
            return "FTM"
        elif chain_id == Network.Moonriver:
            return "MOVR"
        elif chain_id == Network.Arbitrum:
            return "ARB"
        elif chain_id == Network.Avalanche:
            return "AVAX"
        elif chain_id == Network.Harmony:
            return "ONE"
        elif chain_id == Network.Aurora:
            return "AURORA"
        elif chain_id == Network.OKEx:
            return "OKEX"
        elif chain_id == Network.Cronos:
            return "CRO"
        elif chain_id == Network.Optimism:
            return "OPTI"
        elif chain_id == Network.Base:
            return "BASE"

    @staticmethod
    def name(chain_id: Optional[int] = None) -> str:
        """
        Get the full name of a network for a given chain ID.

        If no chain ID is provided, it defaults to the current active chain.

        Args:
            chain_id: The chain ID of the network.

        Examples:
            >>> Network.name(Network.Mainnet)
            'Mainnet'
            >>> Network.name()
            'Mainnet'  # Assuming the current active chain is Mainnet

        See Also:
            :meth:`Network.label` for getting the abbreviation of the network.
        """
        if not chain_id:
            chain_id = _CHAINID

        if chain_id == Network.Mainnet:
            return "Mainnet"
        elif chain_id == Network.BinanceSmartChain:
            return "Binance Smart Chain"
        elif chain_id == Network.Gnosis:
            return "Gnosis"
        elif chain_id == Network.Heco:
            return "Heco"
        elif chain_id == Network.Polygon:
            return "Polygon"
        elif chain_id == Network.Fantom:
            return "Fantom"
        elif chain_id == Network.Moonriver:
            return "Moonriver"
        elif chain_id == Network.Arbitrum:
            return "Arbitrum"
        elif chain_id == Network.Avalanche:
            return "Avalanche"
        elif chain_id == Network.Harmony:
            return "HarmonyOne Shard 0"
        elif chain_id == Network.Aurora:
            return "Aurora"
        elif chain_id == Network.OKEx:
            return "OKEx"
        elif chain_id == Network.Cronos:
            return "Cronos"
        elif chain_id == Network.Optimism:
            return "Optimism"
        elif chain_id == Network.Base:
            return "Base"

    @staticmethod
    def printable(chain_id: Optional[int] = None) -> str:
        """
        Get a printable string that identifies the network.

        If the network is not supported, it returns a generic string with the chain ID.

        Args:
            chain_id: The chain ID of the network.

        Examples:
            >>> Network.printable(Network.Mainnet)
            'Mainnet'
            >>> Network.printable(9999)
            'chain 9999'
        """
        if chain_id is None:
            chain_id = _CHAINID
        return Network.name(chain_id) or f"chain {chain_id}"
