
import abc
import asyncio
from contextlib import suppress
from decimal import Decimal
from functools import cached_property
from logging import getLogger
from typing import (TYPE_CHECKING, Any, Awaitable, List, Literal, NoReturn,
                    Optional, Tuple, Union)

import a_sync
from brownie import chain
from brownie.convert.datatypes import HexString
from brownie.exceptions import ContractNotFound

from y import convert
from y.classes.singleton import ChecksumASyncSingletonMeta
from y.constants import EEE_ADDRESS
from y.contracts import (Contract, build_name, contract_creation_block_async,
                         has_method, probe)
from y.datatypes import Address, AnyAddressType, Block, Pool, UsdPrice
from y.erc20 import decimals, totalSupply
from y.exceptions import (ContractNotVerified, MessedUpBrownieContract,
                          NonStandardERC20)
from y.networks import Network
from y.utils import logging, raw_calls

if TYPE_CHECKING:
    from y.utils.events import Events

logger = getLogger(__name__)

def hex_to_string(h: HexString) -> str:
    '''returns a string from a HexString'''
    h = h.hex().rstrip("0")
    if len(h) % 2 != 0:
        h += "0"
    return bytes.fromhex(h).decode("utf-8")

class ContractBase(a_sync.ASyncGenericBase, metaclass=ChecksumASyncSingletonMeta):
    __slots__ = "address", "asynchronous", "_deploy_block"
    def __init__(
        self, 
        address: AnyAddressType, 
        asynchronous: bool = False, 
        _deploy_block: Optional[int] = None,
    ) -> None:
        self.address = convert.to_address(address)
        self.asynchronous = asynchronous
        self._deploy_block = _deploy_block
        super().__init__()
    
    def __str__(self) -> str:
        return f'{self.address}'

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.address}'"
    
    def __eq__(self, __o: object) -> bool:
        try:
            return convert.to_address(__o) == self.address
        except Exception:
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
        except (ContractNotVerified):
            return False
        except (ContractNotFound, MessedUpBrownieContract):
            return None

    @a_sync.aka.cached_property
    async def build_name(self) -> str:
        return await build_name(self.address, sync=False)

    async def deploy_block(self, when_no_history_return_0: bool = False) -> int:
        if self._deploy_block is None:
            self._deploy_block = await contract_creation_block_async(self.address, when_no_history_return_0=when_no_history_return_0)
        return self._deploy_block
    
    async def has_method(self, method: str, return_response: bool = False) -> Union[bool,Any]:
        return await has_method(self.address, method, return_response=return_response, sync=False)


class ERC20(ContractBase):
    def __repr__(self) -> str:
        cls = self.__class__.__name__
        with suppress(AttributeError):
            if ERC20.symbol.has_cache_value(self):
                symbol = ERC20.symbol.get_cache_value(self)
                return f"<{cls} {symbol} '{self.address}'>"
            elif not asyncio.get_event_loop().is_running() and not self.asynchronous:
                return f"<{cls} {self.symbol} '{self.address}'>"
        return super().__repr__()
    
    @a_sync.aka.cached_property
    async def symbol(self) -> str:
        if self.address == EEE_ADDRESS:
            return "ETH"
        import y._db.utils.token as db
        if symbol := await db.get_symbol(self.address):
            return symbol
        symbol = await self._symbol()
        _tasks.append(asyncio.create_task(coro=db.set_symbol(self.address, symbol), name=f"set_symbol {symbol} for {self.address}"))
        await _clear_finished_tasks()
        return symbol
    
    @a_sync.aka.property
    async def name(self) -> str:
        if self.address == EEE_ADDRESS:
            return "Ethereum"
        import y._db.utils.token as db
        name = await db.get_name(self.address)
        if name:
            return name
        name = await self._name()
        _tasks.append(asyncio.create_task(coro=db.set_name(self.address, name), name=f"set_name {name} for {self.address}"))
        await _clear_finished_tasks()
        return name
    
    @a_sync.aka.cached_property
    async def decimals(self) -> int:
        if self.address == EEE_ADDRESS:
            return 18
        import y._db.utils.token as db
        return await db.get_decimals(self.address)

    @a_sync.a_sync # Override the leading underscore so a_sync lib doesn't bypass this fn
    async def _decimals(self, block: Optional[Block] = None) -> int:
        '''used to fetch decimals at specific block'''
        if self.address == EEE_ADDRESS:
            return 18
        return await decimals(self.address, block=block, sync=False)
    
    @a_sync.aka.cached_property
    async def scale(self) -> int:
        return 10 ** await self.__decimals__(asynchronous=True)
    
    @a_sync.a_sync # Override the leading underscore so a_sync lib doesn't bypass this fn
    async def _scale(self, block: Optional[Block] = None) -> int:
        return 10 ** await self._decimals(block, sync=False)

    async def total_supply(self, block: Optional[Block] = None) -> int:
        return await totalSupply(self.address, block=block, sync=False)

    async def total_supply_readable(self, block: Optional[Block] = None) -> float:
        total_supply, scale = await asyncio.gather(
            self.total_supply(block=block, sync=False),
            self.__scale__(sync=False)
        )
        return total_supply / scale
    
    async def balance_of(self, address: AnyAddressType, block: Optional[Block] = None) -> int:
        return await raw_calls.balanceOf(self.address, address, block=block, sync=False)
    
    async def balance_of_readable(self, address: AnyAddressType, block: Optional[Block] = None) -> float:
        balance, scale = await asyncio.gather(self.balance_of(address, block=block, asynchronous=True), self.__scale__(asynchronous=True))
        return balance / scale

    async def price(
        self, 
        block: Optional[Block] = None, 
        return_None_on_failure: bool = False, 
        ignore_pools: Tuple[Pool, ...] = (),
    ) -> Optional[UsdPrice]:
        from y.prices.magic import get_price
        return await get_price(
            self.address, 
            block=block, 
            fail_to_None=return_None_on_failure,
            ignore_pools=ignore_pools,
            sync=False,
        )
        
    async def _symbol(self) -> str:
        symbol = await probe(self.address, ["symbol()(string)", "SYMBOL()(string)", "getSymbol()(string)"])
        if symbol is None:
            # Sometimes the above will fail if the symbol method returns bytes32, as with MKR. Let's try this.
            symbol = await probe(self.address, ["symbol()(bytes32)"])
            if symbol:
                symbol = hex_to_string(symbol)
        if symbol:
            return symbol
        # we've failed to fetch
        self.__raise_exception('symbol')
    
    async def _name(self) -> str:
        name = await probe(self.address, ["name()(string)", "NAME()(string)", "getName()(string)"])
        if name is None:
            # Sometimes the above will fail if the name method returns bytes32, as with MKR. Let's try this.
            name = await probe(self.address, ["name()(bytes32)"])
            if name:
                name = hex_to_string(name)
        if name:
            return name
        # we've failed to fetch
        self.__raise_exception('name')

    def __raise_exception(self, fn_name: str):
        raise NonStandardERC20(f'''
            Unable to fetch `{fn_name}` for {self.address} on {Network.printable()}
            If the contract is verified, please check to see if it has a strangely named
            `{fn_name}` method and create an issue on https://github.com/BobTheBuidler/ypricemagic
            with the contract address and correct method name so we can keep things going smoothly :)''')


class WeiBalance(a_sync.ASyncGenericBase):
    def __init__(
        self, 
        balance: int,
        token: AnyAddressType,
        block: Optional[Block] = None,
        ignore_pools: Tuple[Pool, ...] = (),
        asynchronous: bool = False,
        ) -> None:

        self.asynchronous = asynchronous
        self.balance = Decimal(balance)
        self.token = ERC20(str(token), asynchronous=self.asynchronous)
        self.block = block
        super().__init__()
        self._logger = logging.get_price_logger(token, block, self.__class__.__name__)
        self._ignore_pools = ignore_pools

    def __str__(self) -> str:
        return str(self.balance)
    
    def __repr__(self) -> str:
        return f"<WeiBalance token={self.token} balance={self.balance} block={self.block}>"

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, int):
            return __o == self.balance
        elif isinstance(__o, WeiBalance):
            return self.balance == __o.balance and self.token == __o.token
        return False
    
    def __lt__(self, __o: object) -> bool:
        if isinstance(__o, int):
            return __o < self.balance
        elif isinstance(__o, WeiBalance):
            if self.token != __o.token:
                raise TypeError(f"'<' only supported between {self.__class__.__name__} instances when denominated in the same token.")
            return self.balance < __o.balance
        raise TypeError(f"'<' not supported between instances of '{self.__class__.__name__}' and '{__o.__class__.__name__}'")

    def __ge__(self, __o: object) -> bool:
        if __o < self:
            return True
        elif type(__o) is type(self):
            return self == __o
        raise TypeError(f"'>=' not supported between instances of '{self.__class__.__name__}' and '{__o.__class__.__name__}'")
    
    @a_sync.aka.property
    async def readable(self) -> float:
        if self.balance == 0:
            return 0
        scale = await self.token.__scale__(sync=False)
        readable = self.balance / scale
        self._logger.debug("balance: %s  decimals: %s  readable: %s", self.balance, str(scale).count("0"), readable)
        return readable
    
    @a_sync.aka.cached_property
    async def value_usd(self) -> float:
        if self.balance == 0:
            return 0
        balance, price = await asyncio.gather(
            self.__readable__(sync=False),
            self.token.price(block=self.block, ignore_pools=self._ignore_pools, sync=False),
        )
        value = balance * Decimal(price)
        self._logger.debug("balance: %s  price: %s  value: %s", balance, price, value)
        return value


_tasks: List[asyncio.Task] = []

async def _clear_finished_tasks() -> None:
    for t in _tasks[:]:
        if t.done():
            await t
            _tasks.remove(t)


class _Loader(ContractBase):
    """Used for use cases where you need to load data thru present time before proceeding, and then continue loading data in the background."""
    __slots__ = "_loaded", "_init_block", "__exc", "__task",
    def __init__(self, address: Address, asynchronous: bool = False):
        super().__init__(address, asynchronous=asynchronous)
        self._init_block = chain.height
        self._loaded = None
        self.__exc = None
        self.__task = None
    @abc.abstractmethod
    async def _load(self) -> NoReturn:
        ...
    @abc.abstractproperty
    def loaded(self) -> Awaitable[Literal[True]]:
        ...
    @property
    def _task(self) -> "asyncio.Task[NoReturn]":
        if self.__exc:
            raise self.__exc
        if self.__task is None:
            logger.debug("creating loader task for %s", self)
            self.__task = asyncio.create_task(coro=self.__load(), name=f"{self}.__load()")
            self.__task.add_done_callback(self._done_callback)
            return self._task
        return self.__task
    def _done_callback(self, task: "asyncio.Task[Any]") -> None:
        if e := task.exception():
            logger.error("exception while loading %s: %s", self, e)
            logger.exception(e)
            self.__exc = e
            self.__task = None
            raise e
    async def __load(self) -> NoReturn:
        """Loads the loader and catches any exceptions"""
        try:
            await self._load()
        except Exception as e:
            self.__exc = e
            raise e


class _EventsLoader(_Loader):
    """Used for use cases where you need to load event data thru present time before proceeding, and then continue loading data in the background."""
    @abc.abstractproperty
    def _events(self) -> "Events":
        ...
    @property
    def loaded(self) -> Awaitable[Literal[True]]:
        if self._loaded is None:
            self._task  # ensure task is running
            self._loaded = asyncio.ensure_future(self._events._lock.wait_for(self._init_block))
        return self._loaded
    async def _load(self) -> NoReturn:
        # TODO: extend this for constant loading
        async for _ in self._events.events(self._init_block):
            pass
