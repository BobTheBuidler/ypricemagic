from abc import abstractmethod
from asyncio import Task, create_task, ensure_future, get_event_loop
from decimal import Decimal
from functools import cached_property
from logging import getLogger
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Generator,
    Literal,
    NoReturn,
    Optional,
    Tuple,
    Union,
    final,
)

import a_sync
from a_sync import cgather
from a_sync.a_sync import HiddenMethodDescriptor
from a_sync.a_sync.method import ASyncBoundMethod
from brownie import Contract, chain, web3
from brownie.convert.datatypes import HexString
from brownie.exceptions import ContractNotFound
from eth_retry import auto_retry
from typing_extensions import Self
from web3.exceptions import ContractLogicError

from y import ENVIRONMENT_VARIABLES as ENVS
from y import convert
from y._decorators import stuck_coro_debugger
from y.classes.singleton import ChecksumASyncSingletonMeta
from y.constants import EEE_ADDRESS
from y.contracts import (
    Contract,
    build_name,
    contract_creation_block_async,
    has_method,
    probe,
)
from y.datatypes import Address, AnyAddressType, Block, Pool, UsdPrice
from y.exceptions import ContractNotVerified, MessedUpBrownieContract, NonStandardERC20
from y.networks import Network
from y.utils import _erc20, logging, raw_calls

if TYPE_CHECKING:
    from y.utils.events import Events

logger = getLogger(__name__)


def hex_to_string(h: HexString) -> str:
    """
    Convert a HexString to a string.

    Args:
        h: The HexString to convert.

    Returns:
        The converted string.
    """
    h = h.hex().rstrip("0")
    if len(h) % 2 != 0:
        h += "0"
    return bytes.fromhex(h).decode("utf-8")


class ContractBase(a_sync.ASyncGenericBase, metaclass=ChecksumASyncSingletonMeta):
    # defaults are stored as class vars to keep instance dicts smaller
    asynchronous: bool = False
    _deploy_block: Optional[int] = None
    __slots__ = ("address",)

    def __init__(
        self,
        address: AnyAddressType,
        *,
        asynchronous: bool = False,
        _deploy_block: Optional[int] = None,
    ) -> None:
        self.address = convert.to_address(address)
        if asynchronous:
            self.asynchronous = asynchronous
        if _deploy_block:
            self._deploy_block = _deploy_block
        super().__init__()

    def __str__(self) -> str:
        """
        Return the contract address as a string.

        Returns:
            The contract address as a string.
        """
        return f"{self.address}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.address}'>"

    def __eq__(self, __o: object) -> bool:
        # Skip checksumming if applicable, its computationally expensive
        if isinstance(__o, str):
            if self.address == __o:
                return True
            try:
                return self.address == convert.to_address(__o)
            except Exception:
                return False
        elif isinstance(__o, (ContractBase, Contract)):
            return self.address == __o.address
        return False

    def __hash__(self) -> int:
        return hash(self.address)

    @property
    def contract(self) -> Contract:
        return Contract(self.address)

    @cached_property
    def _is_cached(self) -> bool:
        try:
            self.contract
            return True
        except ContractNotVerified:
            return False
        except (ContractNotFound, MessedUpBrownieContract):
            return None

    @a_sync.aka.cached_property
    @stuck_coro_debugger
    async def build_name(self) -> str:
        """
        Get the contract's build name.

        Returns:
            The contract's build name.

        Examples:
            >>> contract = ContractBase("0x1234567890abcdef1234567890abcdef12345678")
            >>> await contract.build_name
            'MyContract'
        """
        return await build_name(self.address, sync=False)

    __build_name__: HiddenMethodDescriptor[Self, str]

    @stuck_coro_debugger
    async def deploy_block(self, when_no_history_return_0: bool = False) -> int:
        """
        Get the block number when the contract was deployed.

        Args:
            when_no_history_return_0: If True, return 0 when no history is found instead of raising an exception.

        Returns:
            The block number when the contract was deployed, or 0 if `when_no_history_return_0` is True and the deploy block cannot be determined.

        Examples:
            >>> contract = ContractBase("0x1234567890abcdef1234567890abcdef12345678")
            >>> await contract.deploy_block()
            1234567

        See Also:
            - :func:`contract_creation_block_async`
        """
        if self._deploy_block is None:
            self._deploy_block = await contract_creation_block_async(
                self.address, when_no_history_return_0=when_no_history_return_0
            )
        return self._deploy_block

    deploy_block: ASyncBoundMethod[Self, Any, int]

    async def has_method(
        self, method: str, return_response: bool = False
    ) -> Union[bool, Any]:
        """
        Check if the contract has a specific method.

        Args:
            method: The name of the method to check for.
            return_response: If True, return the response of the method call instead of a boolean.

        Returns:
            A boolean indicating whether the contract has the method, or the response of the method call if return_response is True.

        Examples:
            >>> contract = ContractBase("0x1234567890abcdef1234567890abcdef12345678")
            >>> await contract.has_method("name()")
            True

        See Also:
            - :func:`has_method`
        """
        return await has_method(
            self.address, method, return_response=return_response, sync=False
        )


class ERC20(ContractBase):
    """
    Represents an ERC20 token.
    """

    address: Address
    """
    The contract address of the token.
    """

    def __repr__(self) -> str:
        cls = type(self).__name__
        try:
            if ERC20.symbol.has_cache_value(self):
                symbol = ERC20.symbol.get_cache_value(self)
                return f"<{cls} {symbol} '{self.address}'>"
            elif not get_event_loop().is_running() and not self.asynchronous:
                try:
                    return f"<{cls} {self.__symbol__(sync=True)} '{self.address}'>"
                except NonStandardERC20:
                    return f"<{cls} SYMBOL_INVALID '{self.address}'>"
        except AttributeError:
            pass
        return f"<{cls} SYMBOL_NOT_LOADED '{self.address}'>"

    @a_sync.aka.cached_property
    @stuck_coro_debugger
    async def symbol(self) -> str:
        """
        The token's symbol.

        Returns:
            The token's symbol.

        Examples:
            >>> token = ERC20("0x1234567890abcdef1234567890abcdef12345678")
            >>> await token.symbol
            'TKN'
        """
        if self.address == EEE_ADDRESS:
            return {
                Network.Mainnet: "ETH",
                Network.Fantom: "FTM",
                Network.Polygon: "MATIC",
                Network.Arbitrum: "ETH",
                Network.Optimism: "ETH",
                Network.Base: "ETH",
            }.get(chain.id, "ETH")
        import y._db.utils.token as db

        if symbol := await db.get_symbol(self.address):
            return symbol
        symbol = await self._symbol()
        db.set_symbol(self.address, symbol)
        return symbol

    @a_sync.aka.property
    @stuck_coro_debugger
    async def name(self) -> str:
        """
        The token's name.

        Returns:
            The token's name.

        Examples:
            >>> token = ERC20("0x1234567890abcdef1234567890abcdef12345678")
            >>> await token.name
            'TokenName'
        """
        if self.address == EEE_ADDRESS:
            return "Ethereum"
        import y._db.utils.token as db

        name = await db.get_name(self.address)
        if name:
            return name
        name = await self._name()
        db.set_name(self.address, name)
        return name

    @a_sync.aka.cached_property
    @stuck_coro_debugger
    async def decimals(self) -> int:
        """
        The number of decimal places for the token.

        Returns:
            The number of decimal places for the token.

        Examples:
            >>> token = ERC20("0x1234567890abcdef1234567890abcdef12345678")
            >>> await token.decimals
            18
        """
        if self.address == EEE_ADDRESS:
            return 18
        import y._db.utils.token as db

        try:
            return await db.get_decimals(self.address)
        except ContractLogicError:
            # we've failed to fetch
            self.__raise_exception("decimals")
        except ValueError as e:
            if str(e).endswith(
                "of attr Token.decimals is greater than the maximum allowed value 2147483647"
            ):
                return await self._decimals(sync=False)
            raise

    @a_sync.a_sync  # Override the leading underscore so a_sync lib doesn't bypass this fn
    async def _decimals(self, block: Optional[Block] = None) -> int:
        """used to fetch decimals at specific block"""
        if self.address == EEE_ADDRESS:
            return 18
        try:
            return await _erc20.decimals(self.address, block=block, sync=False)
        except ContractLogicError:
            # we've failed to fetch
            self.__raise_exception("decimals")

    @a_sync.aka.cached_property
    @stuck_coro_debugger
    async def scale(self) -> int:
        """
        Get the scaling factor for the token.

        Returns:
            The scaling factor for the token.

        Examples:
            >>> token = ERC20("0x1234567890abcdef1234567890abcdef12345678")
            >>> await token.scale
            1000000000000000000
        """
        return 10 ** await self.__decimals__

    @a_sync.a_sync  # Override the leading underscore so a_sync lib doesn't bypass this fn
    async def _scale(self, block: Optional[Block] = None) -> int:
        return 10 ** await self._decimals(block, sync=False)

    async def total_supply(self, block: Optional[Block] = None) -> int:
        """
        Get the total supply of the token.

        Args:
            block (optional): The block number to query. Defaults to latest block.

        Returns:
            The total supply of the token.

        Examples:
            >>> token = ERC20("0x1234567890abcdef1234567890abcdef12345678")
            >>> await token.total_supply()
            1000000000000000000000
        """
        return await _erc20.totalSupply(self.address, block=block, sync=False)

    async def total_supply_readable(self, block: Optional[Block] = None) -> float:
        """
        Get the total supply of the token scaled to a human-readable decimal.

        Args:
            block (optional): The block number to query.

        Returns:
            The total supply of the token scaled to a decimal.

        Examples:
            >>> token = ERC20("0x1234567890abcdef1234567890abcdef12345678")
            >>> await token.total_supply_readable()
            1000.0
        """
        total_supply, scale = await cgather(
            self.total_supply(block=block, sync=False), self.__scale__
        )
        return total_supply / scale

    async def balance_of(
        self, address: AnyAddressType, block: Optional[Block] = None
    ) -> int:
        """
        Query the balance of the token for a given address at a specific block.

        Args:
            address: The address to query.
            block (optional): The block number to query. Defaults to latest block.

        Returns:
            The balance of the token held by `address` at block `block`.

        Examples:
            >>> token = ERC20("0x1234567890abcdef1234567890abcdef12345678")
            >>> await token.balance_of("0xabcdefabcdefabcdefabcdefabcdefabcdef")
            500000000000000000000
        """
        return await raw_calls.balanceOf(self.address, address, block=block, sync=False)

    async def balance_of_readable(
        self, address: AnyAddressType, block: Optional[Block] = None
    ) -> float:
        balance, scale = await cgather(
            self.balance_of(address, block=block, sync=False), self.__scale__
        )
        return balance / scale

    async def price(
        self,
        block: Optional[Block] = None,
        return_None_on_failure: bool = False,
        skip_cache: bool = ENVS.SKIP_CACHE,
        ignore_pools: Tuple[Pool, ...] = (),
    ) -> Optional[UsdPrice]:
        """
        Get the price of the token in USD.

        Args:
            block (optional): The block number to query. Defaults to latest block.
            return_None_on_failure: If True, return None instead of raising a :class:`~y.exceptions.yPriceMagicError` on failure.
            skip_cache: If True, skip using the cache while fetching price data.
            ignore_pools: An optional tuple of pools to ignore when calculating the price.

        Returns:
            The price of the token in USD, or None if return_None_on_failure is True and the price cannot be retrieved.

        Raises:
            yPriceMagicError: If return_None_on_failure is False and the price cannot be retrieved.

        Examples:
            >>> token = ERC20("0x1234567890abcdef1234567890abcdef12345678")
            >>> await token.price()
            1.23

        See Also:
            - :func:`y.prices.magic.get_price`
        """
        from y.prices.magic import get_price

        return await get_price(
            self.address,
            block=block,
            fail_to_None=return_None_on_failure,
            skip_cache=skip_cache,
            ignore_pools=ignore_pools,
            sync=False,
        )

    @classmethod
    async def _get_scale_for(cls, address: AnyAddressType) -> Awaitable[int]:
        # We use async ERC20 for memory sake since internal objects are
        # often async and we can avoid duplication 2x a/sync objs
        token = ERC20(address, asynchronous=True)
        try:
            return ERC20.scale.get_cache_value(token)
        except KeyError:
            # We'll use __scale__ instead of scale here for the purposes of optimization
            # We also pass sync kwarg to __scale__ to optimize speed even though async is default
            return await token.__scale__(sync=False)

    async def _symbol(self) -> str:
        """
        Get the token's symbol from the contract.

        Returns:
            The token's symbol.

        Raises:
            NonStandardERC20: If the symbol cannot be retrieved from the contract.

        Examples:
            >>> token = ERC20("0x1234567890abcdef1234567890abcdef12345678")
            >>> await token._symbol()
            'TKN'
        """
        symbol = await probe(
            self.address,
            ("symbol()(string)", "SYMBOL()(string)", "getSymbol()(string)"),
        )
        if symbol is None:
            # Sometimes the above will fail if the symbol method returns bytes32, as with MKR. Let's try this.
            symbol = await probe(self.address, ("symbol()(bytes32)",))
            if symbol:
                symbol = hex_to_string(symbol)
        if symbol:
            return symbol
        # we've failed to fetch
        self.__raise_exception("symbol")

    async def _name(self) -> str:
        """
        Get the token's name from the contract.

        Returns:
            The token's name.

        Raises:
            NonStandardERC20: If the name cannot be retrieved from the contract.

        Examples:
            >>> token = ERC20("0x1234567890abcdef1234567890abcdef12345678")
            >>> await token._name()
            'TokenName'
        """
        name = await probe(
            self.address, ("name()(string)", "NAME()(string)", "getName()(string)")
        )
        if name is None:
            # Sometimes the above will fail if the name method returns bytes32, as with MKR. Let's try this.
            name = await probe(self.address, ("name()(bytes32)",))
            if name:
                name = hex_to_string(name)
        if name:
            return name
        # we've failed to fetch
        self.__raise_exception("name")

    def __raise_exception(self, fn_name: str):
        """
        Raise a NonStandardERC20 exception with a custom error message.

        Args:
            fn_name: The name of the function that failed to retrieve data.

        Raises:
            NonStandardERC20: Always raised with a custom error message.

        Examples:
            >>> token = ERC20("0x1234567890abcdef1234567890abcdef12345678")
            >>> token.__raise_exception("symbol")
            Traceback (most recent call last):
            ...
            y.exceptions.NonStandardERC20: Unable to fetch `symbol` for 0x1234567890abcdef1234567890abcdef12345678 on Mainnet
        """
        raise NonStandardERC20(
            f"""
            Unable to fetch `{fn_name}` for {self.address} on {Network.printable()}
            If the contract is verified, please check to see if it has a strangely named
            `{fn_name}` method and create an issue on https://github.com/BobTheBuidler/ypricemagic
            with the contract address and correct method name so we can keep things going smoothly :)"""
        ) from None

    # These dundermethods are created by a_sync for the async_properties on this class
    __symbol__: HiddenMethodDescriptor[Self, str]
    __name__: HiddenMethodDescriptor[Self, str]
    __decimals__: HiddenMethodDescriptor[Self, int]
    __scale__: HiddenMethodDescriptor[Self, int]


@final
class WeiBalance(a_sync.ASyncGenericBase):
    """
    Represents a balance of a token in wei.

    This class provides utility methods for working with token balances in wei,
    including converting to readable format, getting the price in USD, and performing
    arithmetic operations.
    """

    # defaults are stored as class vars to keep instance dicts smaller
    block: Optional[Block] = None
    asynchronous: bool = False
    _skip_cache: bool = ENVS.SKIP_CACHE
    _ignore_pools: Tuple[Pool, ...] = ()
    __logger = None

    def __init__(
        self,
        balance: int,
        token: AnyAddressType,
        block: Optional[Block] = None,
        *,
        skip_cache: bool = ENVS.SKIP_CACHE,
        ignore_pools: Tuple[Pool, ...] = (),
        asynchronous: bool = False,
    ) -> None:
        """
        Initialize a WeiBalance object.

        Args:
            balance: The balance in wei.
            token: The token address.
            block: The block number for the balance (optional).
            skip_cache: If True, skip using the local cache for price data.
            ignore_pools: A tuple of pools to ignore when calculating the price.
            asynchronous: True if this object will be used with its asynchronous API, False for its sync API.

        Examples:
            >>> balance = WeiBalance(1000000000000000000, "0x1234567890abcdef1234567890abcdef12345678")
            >>> print(balance)
            1000000000000000000
        """
        if asynchronous != self.asynchronous:
            self.asynchronous = asynchronous
        self.balance = Decimal(balance)
        self.token = ERC20(str(token), asynchronous=self.asynchronous)
        if block != self.block:
            self.block = block
        super().__init__()
        if skip_cache != self._skip_cache:
            self._skip_cache = skip_cache
        if ignore_pools != self._ignore_pools:
            self._ignore_pools = ignore_pools

    def __str__(self) -> str:
        """
        Return the balance in wei as a string.

        Returns:
            The balance in wei as a string.

        Examples:
            >>> balance = WeiBalance(1000000000000000000, "0x1234567890abcdef1234567890abcdef12345678")
            >>> str(balance)
            '1000000000000000000'
        """
        return str(self.balance)

    def __repr__(self) -> str:
        return (
            f"<WeiBalance token={self.token} balance={self.balance} block={self.block}>"
        )

    def __hash__(self) -> int:
        return hash(
            (self.balance, self.token, self.block, self._skip_cache, self._ignore_pools)
        )

    def __bool__(self) -> bool:
        """
        Check if the balance is non-zero.

        Returns:
            True if the balance is non-zero, False otherwise.

        Examples:
            >>> balance = WeiBalance(1000000000000000000, "0x1234567890abcdef1234567890abcdef12345678")
            >>> bool(balance)
            True
        """
        return bool(self.balance)

    def __eq__(self, __o: object) -> bool:
        """
        Check if two WeiBalance objects are equal.

        Args:
            __o: The object to compare with.

        Returns:
            True if the objects are equal, False otherwise.

        Examples:
            >>> balance1 = WeiBalance(1000000000000000000, "0x1234567890abcdef1234567890abcdef12345678")
            >>> balance2 = WeiBalance(1000000000000000000, "0x1234567890abcdef1234567890abcdef12345678")
            >>> balance1 == balance2
            True
        """
        if isinstance(__o, int):
            return __o == self.balance
        elif isinstance(__o, WeiBalance):
            return (
                self.balance == __o.balance
                and self.token == __o.token
                and self.block == __o.block
                and self._skip_cache == __o._skip_cache
                and self._ignore_pools == __o._ignore_pools
            )
        return False

    def __lt__(self, __o: object) -> bool:
        if isinstance(__o, int):
            return __o < self.balance
        elif isinstance(__o, WeiBalance):
            if self.token != __o.token:
                raise ValueError(
                    f"'<' only supported between {self.__class__.__name__} instances when denominated in the same token."
                ) from None
            return self.balance < __o.balance
        raise TypeError(
            f"'<' not supported between instances of '{self.__class__.__name__}' and '{__o.__class__.__name__}'"
        ) from None

    def __ge__(self, __o: object) -> bool:
        """
        Check if one WeiBalance object is greater than or equal to another.

        Args:
            __o: The object to compare with.

        Returns:
            True if the current object is greater than or equal to the other object, False otherwise.

        Raises:
            TypeError: If the objects are not of the same type.

        Examples:
            >>> balance1 = WeiBalance(1000000000000000000, "0x1234567890abcdef1234567890abcdef12345678")
            >>> balance2 = WeiBalance(500000000000000000, "0x1234567890abcdef1234567890abcdef12345678")
            >>> balance1 >= balance2
            True
        """
        if __o < self:
            return True
        elif type(__o) is type(self):
            return self == __o
        raise TypeError(
            f"'>=' not supported between instances of '{self.__class__.__name__}' and '{__o.__class__.__name__}'"
        ) from None

    def __radd__(self, __o: Union["WeiBalance", Literal[0]]) -> "WeiBalance":
        if __o == 0:
            return self
        try:
            if self.token != __o.token:
                raise ValueError(
                    f"addition not supported between instances of '{self.__class__.__name__}' and '{__o.__class__.__name__}'"
                ) from None
            if self.block != __o.block:
                raise ValueError(
                    "addition not supported between balances at different block heights"
                ) from None
            if self._skip_cache != __o._skip_cache:
                raise ValueError(
                    "addition not supported between balances with different `_skip_cache` values"
                ) from None
            if self._ignore_pools != __o._ignore_pools:
                raise ValueError(
                    "addition not supported between balances with different `_ignore_pools` values"
                ) from None
            return WeiBalance(
                self.balance - __o.balance,
                self.token,
                self.block,
                skip_cache=self._skip_cache,
                ignore_pools=self._ignore_pools,
            )
        except AttributeError:
            raise TypeError(
                f"right addition not supported between instances of '{type(self).__name__}' and '{type(__o).__name__}'"
            ) from None

    def __add__(self, __o: "WeiBalance") -> "WeiBalance":
        try:
            if self.token != __o.token:
                raise ValueError(
                    f"addition not supported between instances of '{self.__class__.__name__}' and '{__o.__class__.__name__}'"
                ) from None
            if self.block != __o.block:
                raise ValueError(
                    "addition not supported between balances at different block heights"
                ) from None
            if self._skip_cache != __o._skip_cache:
                raise ValueError(
                    "addition not supported between balances with different `_skip_cache` values"
                ) from None
            if self._ignore_pools != __o._ignore_pools:
                raise ValueError(
                    "addition not supported between balances with different `_ignore_pools` values"
                ) from None
            return WeiBalance(
                self.balance - __o.balance,
                self.token,
                self.block,
                skip_cache=self._skip_cache,
                ignore_pools=self._ignore_pools,
            )
        except AttributeError:
            raise TypeError(
                f"addition not supported between instances of '{type(self).__name__}' and '{type(__o).__name__}'"
            ) from None

    def __sub__(self, __o: "WeiBalance") -> "WeiBalance":
        try:
            if self.token != __o.token:
                raise ValueError(
                    f"subtraction not supported between instances of '{self.__class__.__name__}' and '{__o.__class__.__name__}'"
                ) from None
            if self.block != __o.block:
                raise ValueError(
                    "subtraction not supported between balances at different block heights"
                ) from None
            if self._skip_cache != __o._skip_cache:
                raise ValueError(
                    "subtraction not supported between balances with different `_skip_cache` values"
                ) from None
            if self._ignore_pools != __o._ignore_pools:
                raise ValueError(
                    "subtraction not supported between balances with different `_ignore_pools` values"
                ) from None
            return WeiBalance(
                self.balance - __o.balance,
                self.token,
                self.block,
                skip_cache=self._skip_cache,
                ignore_pools=self._ignore_pools,
            )
        except AttributeError:
            raise TypeError(
                f"subtraction not supported between instances of '{type(self).__name__}' and '{type(__o).__name__}'"
            ) from None

    def __mul__(self, __o: Union[int, float, Decimal]) -> "WeiBalance":
        """
        Multiply a WeiBalance object by a scalar value.

        Args:
            __o: The scalar value to multiply by.

        Returns:
            A new WeiBalance object representing the product.

        Raises:
            TypeError: If the scalar value is not a number.

        Examples:
            >>> balance = WeiBalance(1000000000000000000, "0x1234567890abcdef1234567890abcdef12345678")
            >>> balance * 2
            <WeiBalance token=<ERC20 TKN '0x1234567890abcdef1234567890abcdef12345678'> balance=2000000000000000000 block=None>
        """
        if not isinstance(__o, (int, float, Decimal)):
            raise TypeError(
                f"multiplication not supported between instances of '{type(self).__name__}' and '{type(__o).__name__}'"
            ) from None
        return WeiBalance(
            self.balance * Decimal(__o),
            self.token,
            self.block,
            skip_cache=self._skip_cache,
            ignore_pools=self._ignore_pools,
        )

    def __truediv__(self, __o: Union[int, float, Decimal]) -> "WeiBalance":
        """
        Divide a WeiBalance object by a scalar value.

        Args:
            __o: The scalar value to divide by.

        Returns:
            A new WeiBalance object representing the quotient.

        Raises:
            TypeError: If the scalar value is not a number.

        Examples:
            >>> balance = WeiBalance(1000000000000000000, "0x1234567890abcdef1234567890abcdef12345678")
            >>> balance / 2
            <WeiBalance token=<ERC20 TKN '0x1234567890abcdef1234567890abcdef12345678'> balance=500000000000000000 block=None>
        """
        if not isinstance(__o, (int, float, Decimal)):
            raise TypeError(
                f"division not supported between instances of '{type(self).__name__}' and '{type(__o).__name__}'"
            ) from None
        return WeiBalance(
            self.balance / Decimal(__o),
            self.token,
            self.block,
            skip_cache=self._skip_cache,
            ignore_pools=self._ignore_pools,
        )

    @a_sync.aka.property
    async def readable(self) -> Decimal:
        """
        Get the balance scaled to a human-readable decimal.

        Returns:
            The balance scaled to a decimal.

        Examples:
            >>> balance = WeiBalance(1000000000000000000, "0x1234567890abcdef1234567890abcdef12345678")
            >>> await balance.readable
            Decimal('1.0')
        """
        if self.balance == 0:
            return 0
        scale = await self.token.__scale__
        readable = self.balance / scale
        self._logger.debug(
            "balance: %s  decimals: %s  readable: %s",
            self.balance,
            str(scale).count("0"),
            readable,
        )
        return readable

    __readable__: HiddenMethodDescriptor[Self, Decimal]

    @a_sync.aka.property
    async def price(self) -> Decimal:
        """
        Get the price of the token in USD.

        Returns:
            The price of the token in USD.

        Examples:
            >>> balance = WeiBalance(1000000000000000000, "0x1234567890abcdef1234567890abcdef12345678")
            >>> await balance.price
            Decimal('1.23')
        """
        price = Decimal(
            await self.token.price(
                block=self.block,
                skip_cache=self._skip_cache,
                ignore_pools=self._ignore_pools,
                sync=False,
            )
        )
        self._logger.debug("balance: %s  price: %s", self, price)
        return price

    __price__: HiddenMethodDescriptor[Self, Decimal]

    @a_sync.aka.property
    async def value_usd(self) -> Decimal:
        """
        Get the value of the balance in USD.

        Returns:
            The value of the balance in USD.

        Examples:
            >>> balance = WeiBalance(1000000000000000000, "0x1234567890abcdef1234567890abcdef12345678")
            >>> await balance.value_usd
            Decimal('1.23')
        """
        if self.balance == 0:
            return 0
        balance, price = await cgather(self.__readable__, self.__price__)
        value = balance * price
        self._logger.debug("balance: %s  price: %s  value: %s", balance, price, value)
        return value

    __value_usd__: HiddenMethodDescriptor[Self, Decimal]

    @property
    def _logger(self) -> logging.Logger:
        """
        Get the logger for the WeiBalance object.

        Returns:
            The logger for the WeiBalance object.

        Examples:
            >>> balance = WeiBalance(1000000000000000000, "0x1234567890abcdef1234567890abcdef12345678")
            >>> logger = balance._logger
        """
        logger = self.__logger
        if logger is None:
            logger = logging.get_price_logger(
                self.token.address, self.block, extra=self.__class__.__name__
            )
            self.__logger = logger
        return logger


class _Loader(ContractBase):
    """Used for use cases where you need to load data thru present time before proceeding, and then continue loading data in the background."""

    __slots__ = (
        "_loaded",
        "_init_block",
        "__exc",
        "__task",
    )

    def __init__(self, address: Address, *, asynchronous: bool = False):
        super().__init__(address, asynchronous=asynchronous)
        self._init_block = auto_retry(web3.eth.get_block_number)()
        self._loaded = None
        self.__exc = None
        self.__task = None

    def __await__(self) -> Generator[Any, None, Literal[True]]:
        """
        Returns `True` once the `_Loader` has loaded all relevant data thru the current block.

        Returns:
            A generator that yields `True` once the `_Loader` has loaded all relevant data thru the current block.

        Examples:
            >>> loader = _Loader("0x1234567890abcdef1234567890abcdef12345678")
            >>> await loader
            True
        """
        return self.loaded.__await__()

    @abstractmethod
    async def _load(self) -> NoReturn:
        """
        `self._load` is the coro that will run in the daemon task associated with this _Loader.
        Your implementation MUST set Event `self._loaded` once data has been loaded thru the current block, or it will hang indefinitely.
        """

    @property
    def loaded(self) -> Awaitable[Literal[True]]:
        """
        Returns `True` once the `_Loader` has loaded all relevant data thru the current block.

        Returns:
            An awaitable that resolves to `True` once the `_Loader` has loaded all relevant data thru the current block.

        Examples:
            >>> loader = _Loader("0x1234567890abcdef1234567890abcdef12345678")
            >>> await loader.loaded
            True
        """
        self._task  # ensure task is running and not errd
        if self._loaded is None:
            self._loaded = a_sync.Event(name=str(self))
        return self._loaded.wait()

    @property
    def _task(self) -> "Task[NoReturn]":
        """
        The task that runs `self._load()` for this `_Loader`.

        Returns:
            The task that runs `self._load()` for this `_Loader`.

        Raises:
            Exception: If the _Loader has any exception, it is raised.

        Examples:
            >>> loader = _Loader("0x1234567890abcdef1234567890abcdef12345678")
            >>> task = loader._task
        """
        if self.__exc:
            # create a new duplicate exc instead of building a massive traceback on the original
            raise type(self.__exc)(*self.__exc.args).with_traceback(self.__tb)
        if self.__task is None:
            logger.debug("creating loader task for %s", self)
            self.__task = create_task(coro=self.__load(), name=f"{self}.__load()")
            self.__task.add_done_callback(self._done_callback)
        return self.__task

    def _done_callback(self, task: "Task[Any]") -> None:
        """
        Called on `self._task` when it completes, if applicable.

        Args:
            task: The completed task.

        Examples:
            >>> loader = _Loader("0x1234567890abcdef1234567890abcdef12345678")
            >>> loader._done_callback(task)
        """
        if e := task.exception():
            logger.error("exception while loading %s: %s", self, e)
            logger.exception(e)
            self.__task = None

    async def __load(self) -> NoReturn:
        """
        Loads the loader and catches any exceptions.

        Examples:
            >>> loader = _Loader("0x1234567890abcdef1234567890abcdef12345678")
            >>> await loader.__load()
        """
        try:
            await self._load()
        except Exception as e:
            import traceback

            self.__exc = e
            self.__tb = e.__traceback__
            # no need to hold vars in memory
            traceback.clear_frames(self.__tb)
            raise


class _EventsLoader(_Loader):
    """
    Used for use cases where you need to load event data thru present time before proceeding,
    and then continue loading data in the background.
    """

    @property
    @abstractmethod
    def _events(self) -> "Events":
        """
        The Events object associated with this _EventsLoader.
        """

    @property
    def loaded(self) -> Awaitable[Literal[True]]:
        """
        Returns `True` once the `_Loader` has loaded all relevant data thru the current block.

        Returns:
            An awaitable that resolves to `True` once the `_Loader` has loaded all relevant data thru the current block.

        Examples:
            >>> loader = _EventsLoader("0x1234567890abcdef1234567890abcdef12345678")
            >>> await loader.loaded
            True
        """
        self._task  # ensure task is running and not err'd
        if self._loaded is None:
            self._loaded = ensure_future(self._events._lock.wait_for(self._init_block))
        return self._loaded

    async def _load(self) -> NoReturn:
        """
        Load the event data in the background.

        Examples:
            >>> loader = _EventsLoader("0x1234567890abcdef1234567890abcdef12345678")
            >>> await loader._load()
        """
        # TODO: extend this for constant loading
        async for _ in self._events.events(self._init_block):
            pass
