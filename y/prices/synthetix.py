import logging
from typing import Callable, List, Optional

import a_sync
from a_sync import cgather
from a_sync.a_sync import HiddenMethodDescriptor
from eth_typing import ChecksumAddress, HexStr
from multicall import Call
from typing_extensions import Self

from y import convert
from y.constants import CHAINID
from y.contracts import Contract, has_method
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.exceptions import UnsupportedNetwork, call_reverted
from y.networks import Network
from y.utils import a_sync_ttl_cache

try:
    from eth_abi import encode

    encode_bytes: Callable[[str], bytes] = lambda s: encode(["bytes32"], [s.encode()])
except ImportError:
    from eth_abi import encode_single

    encode_bytes: Callable[[str], bytes] = lambda s: encode_single(
        "bytes32", s.encode()
    )

logger = logging.getLogger(__name__)

addresses = {
    Network.Mainnet: "0x823bE81bbF96BEc0e25CA13170F5AaCb5B79ba83",
    Network.Optimism: "0x95A6a3f44a70172E7d50a9e28c85Dfd712756B8C",
}


class Synthetix(a_sync.ASyncGenericSingleton):
    """A class to interact with the Synthetix protocol.

    This class provides methods to interact with the Synthetix protocol,
    allowing users to get contract addresses, synths, and prices.

    Raises:
        UnsupportedNetwork: If the Synthetix protocol is not supported on the current network.

    Examples:
        >>> synthetix = Synthetix(asynchronous=True)
        >>> address = await synthetix.get_address("ProxyERC20")
        >>> print(address)
        <Contract object at 0x...>
    """

    def __init__(self, *, asynchronous: bool = False) -> None:
        if CHAINID not in addresses:
            raise UnsupportedNetwork("synthetix is not supported on this network")
        self.asynchronous = asynchronous
        super().__init__()

    @a_sync.aka.property
    async def address_resolver(self) -> Contract:
        """Get the address resolver contract.

        Returns:
            The address resolver contract.

        Examples:
            >>> resolver = await synthetix.address_resolver
            >>> print(resolver)
            <Contract object at 0x...>
        """
        return await Contract.coroutine(addresses[CHAINID])

    __address_resolver__: HiddenMethodDescriptor[Self, Contract]

    @a_sync.a_sync(ram_cache_maxsize=256)
    async def get_address(self, name: str, block: Block = None) -> Contract:
        """Get contract from Synthetix registry.

        Args:
            name: The name of the contract to retrieve.
            block: The block number to query at. Defaults to the latest block.

        Returns:
            The contract associated with the given name. If the contract is a proxy,
            it returns the target contract if available, otherwise the proxy itself.

        See Also:
            - https://docs.synthetix.io/addresses/

        Examples:
            >>> contract = await synthetix.get_address("ProxyERC20")
            >>> print(contract)
            <Contract object at 0x...>
        """
        address_resolver = await self.__address_resolver__
        address = await address_resolver.getAddress.coroutine(
            encode_bytes(name), block_identifier=block
        )
        proxy = await Contract.coroutine(address)
        return (
            await Contract.coroutine(
                await proxy.target.coroutine(block_identifier=block)
            )
            if hasattr(proxy, "target")
            else proxy
        )

    @a_sync.aka.cached_property
    async def synths(self) -> List[ChecksumAddress]:
        """Get target addresses of all synths.

        Returns:
            A list of target addresses for all synths.

        Examples:
            >>> synths = await synthetix.synths
            >>> print(synths)
            ['0x...', '0x...', ...]
        """
        proxy_erc20 = await self.get_address("ProxyERC20", sync=False)
        synth_count = await proxy_erc20.availableSynthCount
        # Force the addresses to strings so we aren't forced to use brownie's comparison functionality
        synths = [
            ChecksumAddress(synth)
            for synth in await proxy_erc20.availableSynths.map(range(synth_count))
        ]
        logger.info("loaded %s synths", len(synths))
        return synths

    async def is_synth(self, token: AnyAddressType) -> bool:
        """Check if a token is a synth.

        Args:
            token: The token address to check.

        Returns:
            `True` if the token is a synth, `False` if not.

        Raises:
            Exception: If an unexpected error occurs during the check.

        Examples:
            >>> is_synth = await synthetix.is_synth("0x...")
            >>> print(is_synth)
            True

        See Also:
            - :meth:`get_currency_key`
        """
        token = await convert.to_address_async(token)
        try:
            if await synthetix.get_currency_key(token, sync=False):
                return True
            if await has_method(token, "target()(address)", sync=False):
                target = await Call(token, "target()(address)")
                return (
                    target in await synthetix.synths
                    and await Call(target, "proxy()(address)") == token
                )
            return False
        except Exception as e:
            if "invalid jump destination" in str(e):
                return False
            raise

    @a_sync_ttl_cache
    async def get_currency_key(self, token: AnyAddressType) -> Optional[HexStr]:
        """Get the currency key for a given token.

        Args:
            token: The token address to get the currency key for.

        Returns:
            The currency key as a hex string, or `None` if not found.

        Examples:
            >>> currency_key = await synthetix.get_currency_key("0x...")
            >>> print(currency_key)
            '0x...'
        """
        target = (
            await Call(token, "target()(address)")
            if await has_method(token, "target()(address)", sync=False)
            else token
        )
        return (
            await Call(target, "currencyKey()(bytes32)")
            if await has_method(token, "currencyKey()(bytes32)", sync=False)
            else None
        )

    async def get_price(
        self, token: AnyAddressType, block: Optional[Block] = None
    ) -> Optional[UsdPrice]:
        """Get the price of a synth in dollars.

        Args:
            token: The token address to get the price for.
            block: The block number to query at. Defaults to the latest block.

        Returns:
            The price of the synth in USD, or `None` if the price is stale.

        Raises:
            Exception: If an unexpected error occurs during the price retrieval.

        Examples:
            >>> price = await synthetix.get_price("0x...")
            >>> print(price)
            1.23

        See Also:
            - :meth:`get_currency_key`
        """
        token = await convert.to_address_async(token)
        rates, key = await cgather(
            self.get_address("ExchangeRates", block=block, sync=False),
            self.get_currency_key(token, sync=False),
        )
        if await rates.rateIsStale.coroutine(key, block_identifier=block):
            return None
        try:
            return UsdPrice(
                await rates.rateForCurrency.coroutine(
                    key, block_identifier=block, decimals=18
                )
            )
        except Exception as e:
            if not call_reverted(e):
                raise


synthetix = Synthetix(asynchronous=True) if CHAINID in addresses else set()
