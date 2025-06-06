from asyncio import sleep
from contextlib import suppress
from decimal import Decimal
from logging import DEBUG, getLogger
from typing import Any, AsyncIterator, Dict, List, Optional, Set, Tuple

import a_sync
import a_sync.exceptions
import brownie
import dank_mids
from a_sync import cgather
from a_sync.a_sync import HiddenMethodDescriptor
from brownie.network.event import _EventItem
from dank_mids.exceptions import Revert
from eth_typing import HexAddress
from eth_utils.toolz import concat
from multicall import Call
from typing_extensions import Self
from web3.exceptions import ContractLogicError

from y import ENVIRONMENT_VARIABLES as ENVS
from y import convert
from y._decorators import continue_on_revert, stuck_coro_debugger
from y.classes.common import ERC20, ContractBase, WeiBalance
from y.constants import (
    CHAINID,
    CONNECTED_TO_MAINNET,
    STABLECOINS,
    WRAPPED_GAS_COIN,
    sushi,
    usdc,
    weth,
)
from y.contracts import Contract, contract_creation_block_async
from y.datatypes import (
    Address,
    AddressOrContract,
    AnyAddressType,
    Block,
    Pool,
    UsdPrice,
)
from y.exceptions import (
    CantFindSwapPath,
    ContractNotVerified,
    NonStandardERC20,
    NotAUniswapV2Pool,
    TokenNotFound,
    call_reverted,
    continue_if_call_reverted,
    reraise_excs_with_extra_context,
)
from y.interfaces.uniswap.factoryv2 import UNIV2_FACTORY_ABI
from y.networks import Network
from y.prices import magic
from y.prices.dex.uniswap.v2_forks import (
    ROUTER_TO_FACTORY,
    ROUTER_TO_PROTOCOL,
    special_paths,
)
from y.utils.events import ProcessedEvents
from y.utils.raw_calls import raw_call

logger = getLogger(__name__)

Path = List[AddressOrContract]
Reserves = Tuple[int, int, int]

factory_helper_address = {
    # put special case addresses here
}.get(CHAINID, "0xE57Bfd650A7771E401d56d4b2CA22d9f8f51D3D9")

try:
    FACTORY_HELPER = Contract(factory_helper_address)
except ContractNotVerified:
    FACTORY_HELPER = None


class UniswapV2Pool(ERC20):
    """
    Represents a liquidity pool from Uniswap V2 or its forks.

    This class provides methods to interact with and retrieve information
    about a Uniswap V2 or fork liquidity pool, such as token reserves,
    total value locked (TVL), and price calculations.

    Examples:
        >>> pool = UniswapV2Pool("0xAddress")
        >>> reserves = await pool.reserves()
        >>> price = await pool.get_price()
        >>> tvl = await pool.tvl()

    See Also:
        - :class:`~y.classes.common.ERC20`
        - :class:`~y.prices.dex.uniswap.v2_forks`
    """

    # default stored as class var to keep instance dicts smaller
    __types_assumed = True
    "True if we're assuming types based on normal univ2 abi, False if we checked via block explorer."

    __slots__ = ("get_reserves",)

    def __init__(
        self,
        address: AnyAddressType,
        token0: Optional[Address] = None,
        token1: Optional[Address] = None,
        deploy_block: Optional[int] = None,
        asynchronous: bool = False,
    ):
        super().__init__(address, asynchronous=asynchronous)
        self.get_reserves = Call(self.address, "getReserves()((uint112,uint112,uint32))").coroutine
        if deploy_block:
            self._deploy_block = deploy_block
        if token0:
            self.token0 = token0
        if token1:
            self.token1 = token1

    @a_sync.aka.cached_property
    async def factory(self) -> Address:
        try:
            return await raw_call(self.address, "factory()", output="address", sync=False)
        except ValueError as e:
            if call_reverted(e):
                raise NotAUniswapV2Pool(self) from e
            # `is not a valid ETH address` means we got some kind of response from the chain.
            # but couldn't convert to address. If it happens to be a goofy but
            # verified uni fork, maybe we can get factory this way
            okay_errors = [
                "is not a valid ETH address",
                "invalid opcode",
                "invalid jump destination",
            ]
            if all(msg not in str(e) for msg in okay_errors):
                raise
            contract = await Contract.coroutine(self.address)
            try:
                return await contract.factory
            except AttributeError as exc:
                raise NotAUniswapV2Pool(self) from exc

    __factory__: HiddenMethodDescriptor[Self, Address]

    @a_sync.aka.cached_property
    async def tokens(self) -> Tuple[ERC20, ERC20]:
        return await cgather(self.__token0__, self.__token1__)

    __tokens__: HiddenMethodDescriptor[Self, Tuple[ERC20, ERC20]]

    @a_sync.aka.cached_property
    async def token0(self) -> ERC20:
        try:
            if token0 := await Call(self.address, "token0()(address)"):
                return ERC20(token0, asynchronous=self.asynchronous)
        except ValueError as e:
            continue_if_call_reverted(e)
        raise NotAUniswapV2Pool(self)

    __token0__: HiddenMethodDescriptor[Self, ERC20]

    @a_sync.aka.cached_property
    async def token1(self) -> ERC20:
        try:
            if token1 := await Call(self.address, "token1()(address)"):
                return ERC20(token1, asynchronous=self.asynchronous)
        except ValueError as e:
            continue_if_call_reverted(e)
        raise NotAUniswapV2Pool(self)

    __token1__: HiddenMethodDescriptor[Self, ERC20]

    @a_sync.a_sync(ram_cache_ttl=ENVS.CACHE_TTL)
    @stuck_coro_debugger
    async def get_price(
        self, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE
    ) -> Optional[UsdPrice]:
        """
        Calculate the price of the pool's liquidity token in USD.

        This method calculates the price of the pool's liquidity token by dividing
        the total value locked (TVL) by the total supply of the liquidity token.

        Args:
            block: The block number to query. Defaults to the latest block.
            skip_cache: If True, skip using the cache while fetching price data.

        Examples:
            >>> pool = UniswapV2Pool("0xAddress")
            >>> price = await pool.get_price()
            >>> print(price)

        See Also:
            - :meth:`tvl`
            - :meth:`total_supply_readable`
        """
        tvl = await self.tvl(block=block, skip_cache=skip_cache, sync=False)
        if tvl is not None:
            return UsdPrice(
                tvl / Decimal(await self.total_supply_readable(block=block, sync=False))
            )

    @a_sync.a_sync(ram_cache_maxsize=None, ram_cache_ttl=ENVS.CACHE_TTL)
    async def get_token_out(self, token_in: Address) -> ERC20:
        token0, token1 = await self.__tokens__
        if token_in == token0:
            # these return instantly since theyre already cached
            return token1
        elif token_in == token1:
            # these return instantly since theyre already cached
            return token0
        raise TokenNotFound(token_in, [token0, token1]) from None

    @stuck_coro_debugger
    async def reserves(
        self, *, block: Optional[Block] = None
    ) -> Optional[Tuple[WeiBalance, WeiBalance]]:
        try:
            reserves = await self.get_reserves(block_id=block)
        except Exception as e:
            if not call_reverted(e):
                raise
            reserves = None

        if reserves is None and self.__types_assumed:
            try:
                await self._check_return_types()
            except AttributeError as e:
                raise NotAUniswapV2Pool(self) from e
            return await self.reserves(block=block, sync=False)

        if reserves is None and self._verified:
            # This shouldn't really run anymore, maybe delete
            contract = await Contract.coroutine(self.address)
            try:
                reserves = await contract.getReserves.coroutine(block_identifier=block)
                types = ",".join(output["type"] for output in contract.getReserves.abi["outputs"])
                logger.warning(f"abi for getReserves for {contract} is {types}")
            except Exception as e:
                if not call_reverted(e):
                    raise

        if reserves is None:
            return None

        return tuple(
            WeiBalance(balance, token, block=block)
            for balance, token in zip(reserves, await self.__tokens__)
        )

    @stuck_coro_debugger
    async def tvl(
        self, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE
    ) -> Optional[Decimal]:
        """
        Calculate the total value locked (TVL) in the pool in USD.

        This method calculates the TVL by summing the USD value of the reserves
        of the two tokens in the pool.

        Args:
            block: The block number to query. Defaults to the latest block.
            skip_cache: If True, skip using the cache while fetching price data.

        Examples:
            >>> pool = UniswapV2Pool("0xAddress")
            >>> tvl = await pool.tvl()
            >>> print(tvl)

        See Also:
            - :meth:`reserves`
            - :meth:`get_price`
        """
        # start these tasks now
        price_tasks: a_sync.TaskMapping[ERC20, UsdPrice]
        price_tasks = ERC20.price.map(
            await self.__tokens__,
            block=block,
            return_None_on_failure=True,
            skip_cache=skip_cache,
        )

        reserves: Tuple[WeiBalance, WeiBalance]
        if (reserves := await self.reserves(block=block, sync=False)) is None:
            await price_tasks.close()
            return None

        prices = await price_tasks.values(pop=True)
        if vals := [
            Decimal(await reserve.__readable__) * Decimal(price)
            for reserve, price in zip(reserves, prices)
            if price is not None
        ]:
            if len(vals) == 1:
                vals *= 2
            if len(vals) == 2:
                if logger.isEnabledFor(DEBUG):
                    log_debug("reserves: %s", reserves)
                    log_debug("prices: %s", prices)
                    log_debug("vals: %s", vals)
                return sum(vals)
            else:
                raise Exception("how did we get here?") from None

    @stuck_coro_debugger
    @a_sync.a_sync(
        ram_cache_maxsize=100_000, ram_cache_ttl=60 * 60, semaphore=10_000
    )  # lets try a semaphore here
    async def check_liquidity(self, token: Address, block: Block) -> int:
        """
        Check the liquidity of a specific token in the pool at a given block.

        Args:
            token: The address of the token to check.
            block: The block number to query.

        Returns:
            The liquidity of the token in the pool.

        Raises:
            TokenNotFound: If the token is not one of the two tokens in the liquidity pool.

        Examples:
            >>> pool = UniswapV2Pool("0xAddress")
            >>> liquidity = await pool.check_liquidity("0xTokenAddress", 12345678)
            >>> print(liquidity)
        """
        if debug_logs := logger.isEnabledFor(DEBUG):
            # get symbol cached into memcache to make pool more identifiable in logs
            await self.__symbol__
            log_debug(
                "checking %s liquidity for %s %s at %s",
                repr(self),
                await ERC20(token, asynchronous=True).symbol,
                token,
                block,
            )
        if block and block < await self.deploy_block(sync=False):
            if debug_logs:
                log_debug("block %s is before %s deploy block", block, self)
            return 0
        if reserves := await self.reserves(block=block, sync=False):
            balance: WeiBalance
            for balance in reserves:
                if token == balance.token:
                    liquidity = balance.balance
                    await log_liquidity(self, token, block, liquidity, debug_logs)
                    return liquidity
            raise TokenNotFound(token, reserves)
        return 0

    @stuck_coro_debugger
    async def is_uniswap_pool(self, block: Optional[Block] = None) -> bool:
        """
        Check if this contract is a valid liquidity pool for Uniswap V2 or one of its forks.

        Args:
            block (optional): The block number to query. Defaults to latest block.

        Returns:
            True if the contract is a valid Uniswap V2 pool, False otherwise.

        Examples:
            >>> pool = UniswapV2Pool("0xAddress")
            >>> is_valid = await pool.is_uniswap_pool()
            >>> print(is_valid)
        """
        try:
            return all(
                await cgather(
                    self.reserves(block=block, sync=False),
                    self.total_supply(block, sync=False),
                )
            )
        except (NotAUniswapV2Pool, ContractNotVerified):
            return False

    async def _check_return_types(self) -> None:
        if not self.__types_assumed:
            return
        try:
            contract = await Contract.coroutine(self.address)
            reserves_types = ",".join(
                output["type"] for output in contract.getReserves.abi["outputs"]
            )
            self._verified = True
            assert reserves_types.count(",") == 2, reserves_types
            self.get_reserves = Call(self.address, f"getReserves()(({reserves_types}))").coroutine
        except ContractNotVerified:
            self._verified = False
        self.__types_assumed = False


class PoolsFromEvents(ProcessedEvents[UniswapV2Pool]):
    PairCreated = "0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9"
    __slots__ = "asynchronous", "label"

    def __init__(self, factory: AnyAddressType, label: str, asynchronous: bool = False):
        self.asynchronous = asynchronous
        self.label = label
        super().__init__(addresses=[factory], topics=[[self.PairCreated]], is_reusable=False)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} label={self.label}>"

    def pools(self, to_block: Optional[int] = None) -> AsyncIterator[UniswapV2Pool]:
        return self._objects_thru(block=to_block)

    def _get_block_for_obj(self, obj: UniswapV2Pool) -> int:
        return obj._deploy_block

    def _process_event(self, event: _EventItem) -> UniswapV2Pool:
        pool = UniswapV2Pool(
            address=event["pair"],
            token0=event["token0"],
            token1=event["token1"],
            asynchronous=self.asynchronous,
        )
        # Do this here instead of in the init in case the user inited their own UniswapV2Pool object previoulsy, which is now the singleton
        pool._deploy_block = event.block_number
        return pool


def _log_factory_helper_failure(e: Exception, token_address, block, _ignore_pools) -> None:
    stre = f"{e}".lower()
    if "timeout" in stre:
        msg = "timeout"
    elif "out of gas" in stre:
        msg = "out of gas"
    elif "invalid request" in stre:
        # TODO: debug where these come from
        msg = "invalid request"
    elif isinstance(e, (Revert, ContractLogicError)):
        # TODO: debug me!
        msg = "reverted"
    else:
        raise e

    logger.debug(
        "helper %s for %s at block %s ignore_pools %s: %s",
        msg,
        token_address,
        block,
        _ignore_pools,
        e,
    )


_all_pools_semaphore = a_sync.Semaphore(10, name=f"{__name__}.UniswapRouterV2.all_pools_for")


class UniswapRouterV2(ContractBase):
    def __init__(self, router_address: AnyAddressType, *, asynchronous: bool = False) -> None:
        super().__init__(router_address, asynchronous=asynchronous)

        self.label = ROUTER_TO_PROTOCOL[self.address]
        self.factory = ROUTER_TO_FACTORY[self.address]
        self.special_paths = special_paths(self.address)
        self.get_amounts_out = Call(self.address, "getAmountsOut(uint,address[])(uint[])").coroutine
        self._skip_factory_helper: Set[Address] = set()

        # we need the factory contract object cached in brownie so we can decode logs properly
        if not ContractBase(self.factory, asynchronous=self.asynchronous)._is_cached:
            brownie.Contract.from_abi("UniClone Factory [forced]", self.factory, UNIV2_FACTORY_ABI)

        self._supports_factory_helper = (
            CHAINID
            not in (
                Network.Mainnet,  # Too many pools for the helper
                Network.Arbitrum,  # Arbi nodes timeout often while using helper
                Network.Base,  # Base has too many pools for the helper at this point
            )
            and FACTORY_HELPER
            and self.label
            and self.label not in {"zipswap"}
        )

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"<UniswapV2Router {self.label} '{self.address}'>"

    @stuck_coro_debugger
    @a_sync.a_sync(ram_cache_maxsize=500)
    async def get_price(
        self,
        token_in: Address,
        block: Optional[Block] = None,
        token_out: Address = usdc.address,
        paired_against: Address = WRAPPED_GAS_COIN,
        skip_cache: bool = ENVS.SKIP_CACHE,
        ignore_pools: Tuple[Pool, ...] = (),
    ) -> Optional[UsdPrice]:
        """
        Calculate a price based on Uniswap Router quote for selling one `token_in`.
        Always uses intermediate WETH pair if `[token_in,weth,token_out]` swap path available.
        """

        token_in, token_out, path = str(token_in), str(token_out), None

        if CHAINID == Network.BinanceSmartChain and token_out == usdc.address:
            busd = await Contract.coroutine("0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56")
            token_out = busd.address

        if token_in in STABLECOINS:
            return 1

        try:
            amount_in = await ERC20._get_scale_for(token_in)
        except NonStandardERC20:
            return None

        debug_logs = logger.isEnabledFor(DEBUG)

        if token_in in [weth.address, WRAPPED_GAS_COIN] and token_out in STABLECOINS:
            path = [token_in, token_out]

        elif str(token_out) in STABLECOINS:
            with suppress(CantFindSwapPath):
                path = await self.get_path_to_stables(
                    token_in, block, _ignore_pools=ignore_pools, sync=False
                )
                if debug_logs:
                    log_debug("smrt")

        # If we can't find a good path to stables, we might still be able to determine price from price of paired token
        if path is None and (
            deepest_pool := await self.deepest_pool(
                token_in, block, _ignore_pools=ignore_pools, sync=False
            )
        ):
            if debug_logs:
                log_debug("deepest pool: %s", deepest_pool)
            paired_with = await deepest_pool.get_token_out(token_in, sync=False)
            path = [token_in, paired_with]
            quote, out_scale = await cgather(
                self.get_quote(amount_in, path, block=block, sync=False),
                ERC20._get_scale_for(path[-1]),
            )
            if debug_logs:
                log_debug("quote: %s", quote)
            if quote is not None:
                amount_out = Decimal(quote[-1]) / out_scale
                fees = Decimal(0.997) ** (len(path) - 1)
                amount_out /= fees
                paired_with_price = await magic.get_price(
                    paired_with,
                    block,
                    fail_to_None=True,
                    skip_cache=skip_cache,
                    ignore_pools=(*ignore_pools, deepest_pool),
                    sync=False,
                )

                if paired_with_price:
                    return amount_out * Decimal(paired_with_price)

        # If we still don't have a workable path, try this smol brain method
        if path is None:
            path = self._smol_brain_path_selector(token_in, token_out, paired_against)
            # NOTE: does this ever run anymore? can we take it out?
            logger.warning("using smol brain path selector")

        fees = 0.997 ** (len(path) - 1)
        if debug_logs:
            log_debug("router: %s     path: %s", self.label, path)
        quote, out_scale = await cgather(
            self.get_quote(amount_in, path, block=block, sync=False),
            ERC20._get_scale_for(path[-1]),
        )
        if quote is not None:
            amount_out = quote[-1] / out_scale
            return UsdPrice(amount_out / fees)

    @continue_on_revert
    @stuck_coro_debugger
    async def get_quote(
        self, amount_in: int, path: Path, block: Optional[Block] = None
    ) -> Tuple[int, int]:
        if not self._is_cached:
            return await self.get_amounts_out((amount_in, path), block_id=block)
        try:
            return await self.contract.getAmountsOut.coroutine(
                amount_in, path, block_identifier=block
            )
        # TODO figure out how to best handle uni forks with slight modifications.
        # Sometimes the below "else" code will not work with modified methods. Brownie works for now.
        except Exception as e:
            strings = [
                "INSUFFICIENT_INPUT_AMOUNT",
                "INSUFFICIENT_LIQUIDITY",
                "INSUFFICIENT_OUT_LIQUIDITY",
                "Sequence has incorrect length",
            ]
            if not call_reverted(e) and all(s not in str(e) for s in strings):
                raise

    @a_sync.aka.cached_property
    @stuck_coro_debugger
    async def pools(self) -> List[UniswapV2Pool]:
        logger.info(
            "Fetching pools for %s on %s. If this is your first time using ypricemagic, this can take a while. Please wait patiently...",
            self.label,
            Network.printable(),
        )
        factory = self.factory
        events = PoolsFromEvents(factory, self.label, asynchronous=self.asynchronous)
        to_block = await dank_mids.eth.block_number
        pools = [pool async for pool in events.pools(to_block=to_block)]
        events._task.cancel()
        del events
        all_pairs_len = await raw_call(factory, "allPairsLength()", output="int", sync=False)
        if len(pools) > all_pairs_len:
            raise NotImplementedError("this shouldnt happen again")
        elif to_get := all_pairs_len - len(pools):  # <
            logger.debug(
                "Oh no! Looks like your node can't look back that far. Checking for the missing %s pools...",
                to_get,
            )
            factory = await Contract.coroutine(self.factory)
            for i, pool_address in enumerate(await factory.allPairs.map(range(to_get))):
                pool = UniswapV2Pool(address=pool_address, asynchronous=self.asynchronous)
                pools.insert(i, pool)
            logger.debug("Done fetching %s missing pools on %s", to_get, self.label)

        tokens = set(concat(await UniswapV2Pool.tokens.map(pools).values(pop=True)))

        logger.info(
            "Loaded %s pools supporting %s tokens on %s",
            len(pools),
            len(tokens),
            self.label,
        )
        return pools

    __pools__: HiddenMethodDescriptor[Self, List[UniswapV2Pool]]

    @stuck_coro_debugger
    @a_sync.a_sync(ram_cache_maxsize=None, semaphore=_all_pools_semaphore)
    async def all_pools_for(self, token_in: Address) -> Dict[UniswapV2Pool, Address]:
        pool_to_token_out = {}
        for i, pool in enumerate(await self.__pools__):
            # this will return immediately since the pools are already loaded by this point
            token0, token1 = await pool.__tokens__
            if token_in == token0:
                pool_to_token_out[pool] = token1
            elif token_in == token1:
                pool_to_token_out[pool] = token0
            if not i % 10_000:
                await sleep(0)
        return pool_to_token_out

    @stuck_coro_debugger
    async def get_pools_for(
        self, token_in: Address, block: Optional[Block] = None
    ) -> Dict[UniswapV2Pool, Address]:
        if self._supports_factory_helper is False or token_in in self._skip_factory_helper:
            return await self.all_pools_for(token_in, sync=False)
        try:
            pools: List[HexAddress] = await FACTORY_HELPER.getPairsFor.coroutine(
                self.factory, token_in, block_identifier=block
            )
        except Exception as e:
            okay_errs = "out of gas", "timeout"
            stre = str(e).lower()
            if "invalid request" in stre:
                # TODO: debug where this invalid request is coming from
                self._skip_factory_helper.add(token_in)
            elif call_reverted(e) or any(err in stre for err in okay_errs):
                pass
            else:
                raise
            return await self.all_pools_for(token_in, sync=False)

        pool_to_token_out = {}
        for p in pools:
            pool = UniswapV2Pool(p, asynchronous=self.asynchronous)
            # this will return immediately since the pools are already loaded by this point
            token0, token1 = await pool.__tokens__
            if token_in == token0:
                pool_to_token_out[pool] = token1
            elif token_in == token1:
                pool_to_token_out[pool] = token0
        return pool_to_token_out

    @stuck_coro_debugger
    async def pools_for_token(
        self,
        token_address: Address,
        block: Optional[Block] = None,
        _ignore_pools: Tuple[UniswapV2Pool, ...] = (),
    ) -> AsyncIterator[UniswapV2Pool]:
        pools: Dict[UniswapV2Pool, Address]

        if (
            CONNECTED_TO_MAINNET
            and token_address == WRAPPED_GAS_COIN
            and self.label == "uniswap v2"
        ):
            # This will run out of gas if we use the helper so we bypass it with a known liquid pool
            usdc_pool = UniswapV2Pool(
                "0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc", asynchronous=True
            )
            pools = {usdc_pool: "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"}
        elif (
            CHAINID == Network.Base
            and token_address == WRAPPED_GAS_COIN
            and self.label == "uniswap v2"
        ):
            # This will run out of gas if we use the helper so we bypass it with a known liquid pool
            usdc_pool = UniswapV2Pool(
                "0x88A43bbDF9D098eEC7bCEda4e2494615dfD9bB9C", asynchronous=True
            )
            usdbc_pool = UniswapV2Pool(
                "0xe902EF54E437967c8b37D30E80ff887955c90DB6", asynchronous=True
            )
            pools = {
                usdc_pool: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
                usdbc_pool: "0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA",
            }
        else:
            pools = await self.get_pools_for(token_address, block=block, sync=False)

        if _ignore_pools:
            pools = pools.copy()
            for pool in _ignore_pools:
                pools.pop(pool, None)

        if not pools:
            return

        elif block is None:
            for pool in pools:
                yield pool
            return

        async for pool, deploy_block in ERC20.deploy_block.map(when_no_history_return_0=True).map(
            pools
        ):
            if deploy_block <= block:
                yield pool

    @stuck_coro_debugger
    @a_sync.a_sync(ram_cache_maxsize=500)
    async def deepest_pool(
        self,
        token_address: AnyAddressType,
        block: Optional[Block] = None,
        _ignore_pools: Tuple[UniswapV2Pool, ...] = (),
    ) -> Optional[UniswapV2Pool]:
        """returns the deepest pool for `token_address` at `block`, excluding pools in `_ignore_pools`"""
        token_address = await convert.to_address_async(token_address)
        if token_address == WRAPPED_GAS_COIN or token_address in STABLECOINS:
            return await self.deepest_stable_pool(token_address, block, sync=False)
        if self._supports_factory_helper and (
            block is None or block >= await contract_creation_block_async(FACTORY_HELPER)
        ):
            try:
                deepest_pool, deepest_pool_depth = await self.deepest_pool_for(
                    token_address, block, ignore_pools=_ignore_pools
                )
                return (
                    None
                    if deepest_pool == brownie.ZERO_ADDRESS
                    else UniswapV2Pool(deepest_pool, asynchronous=self.asynchronous)
                )
            except (Revert, ValueError, ContractLogicError) as e:
                if "invalid request" in str(e):
                    self._skip_factory_helper.add(token_address)
                _log_factory_helper_failure(e, token_address, block, _ignore_pools)

        pools = self.pools_for_token(token_address, block, _ignore_pools=_ignore_pools)
        if logger.isEnabledFor(DEBUG):
            log_debug(
                "checking %s %s liquidity at block %s for pools %s",
                await ERC20(token_address, asynchronous=True).symbol,
                token_address,
                block,
                pools,
            )

        deepest_pool: UniswapV2Pool
        async for deepest_pool in (
            UniswapV2Pool.check_liquidity.map(pools, token=token_address, block=block)
            .keys(pop=True)
            .aiterbyvalues(reverse=True)
        ):
            return deepest_pool

    @stuck_coro_debugger
    @a_sync.a_sync(ram_cache_maxsize=500)
    async def deepest_stable_pool(
        self,
        token_address: AnyAddressType,
        block: Optional[Block] = None,
        _ignore_pools: Tuple[UniswapV2Pool, ...] = (),
    ) -> Optional[UniswapV2Pool]:
        """returns the deepest pool for `token_address` at `block` which has `token_address` paired with a stablecoin, excluding pools in `_ignore_pools`"""
        token_out_tasks: a_sync.TaskMapping[UniswapV2Pool, ERC20]
        deepest_stable_pool: UniswapV2Pool
        token_address = await convert.to_address_async(token_address)
        pools = self.pools_for_token(token_address, block=block, _ignore_pools=_ignore_pools)
        token_out_tasks = UniswapV2Pool.get_token_out.map(token_in=token_address)
        if stable_pools := [
            pool
            async for pool, paired_with in token_out_tasks.map(pools)
            if paired_with in STABLECOINS
        ]:
            del token_out_tasks

            if self._supports_factory_helper and (
                block is None
                or block
                >= await contract_creation_block_async(
                    FACTORY_HELPER, when_no_history_return_0=True
                )
            ):
                (
                    deepest_stable_pool,
                    deepest_stable_pool_balance,
                ) = await FACTORY_HELPER.deepestPoolForFrom.coroutine(
                    token_address, stable_pools, block_identifier=block
                )
                return (
                    None
                    if deepest_stable_pool == brownie.ZERO_ADDRESS
                    else UniswapV2Pool(deepest_stable_pool, asynchronous=self.asynchronous)
                )

            async for deepest_stable_pool, depth in (
                UniswapV2Pool.check_liquidity.map(stable_pools, token=token_address, block=block)
                .items(pop=True)
                .aiterbyvalues(reverse=True)
            ):
                return deepest_stable_pool

    @stuck_coro_debugger
    @a_sync.a_sync(ram_cache_maxsize=500)
    async def get_path_to_stables(
        self,
        token: AnyAddressType,
        block: Optional[Block] = None,
        _loop_count: int = 0,
        _ignore_pools: Tuple[UniswapV2Pool, ...] = (),
    ) -> Path:
        if _loop_count > 10:
            raise CantFindSwapPath
        token_address = await convert.to_address_async(token)
        path = [token_address]
        deepest_pool = await self.deepest_pool(token_address, block, _ignore_pools, sync=False)
        if deepest_pool:
            paired_with = await deepest_pool.get_token_out(token_address, sync=False)
            from y.prices.utils.buckets import check_bucket

            if await check_bucket(paired_with, sync=False) and _loop_count == 0:
                # let's just use the other token to get the price
                return None
            deepest_stable_pool = await self.deepest_stable_pool(
                token_address, block, _ignore_pools=_ignore_pools, sync=False
            )
            if deepest_stable_pool and deepest_pool == deepest_stable_pool:
                path.append(await deepest_stable_pool.get_token_out(token_address, sync=False))
                return path

            if path == [token_address]:
                with suppress(CantFindSwapPath):
                    path.extend(
                        await self.get_path_to_stables(
                            paired_with,
                            block=block,
                            _loop_count=_loop_count + 1,
                            _ignore_pools=tuple(list(_ignore_pools) + [deepest_pool]),
                            sync=False,
                        )
                    )

        if path == [token_address]:
            raise CantFindSwapPath(
                f"Unable to find swap path for {token_address} on {Network.printable()}"
            )

        return path

    @stuck_coro_debugger
    @a_sync.a_sync(ram_cache_maxsize=100_000, ram_cache_ttl=60 * 60)
    async def check_liquidity(self, token: Address, block: Block, ignore_pools=[]) -> int:
        if debug_logs := logger.isEnabledFor(DEBUG):
            log_debug(
                "checking %s liquidity for %s %s at %s",
                self,
                await ERC20(token, asynchronous=True).symbol,
                token,
                block,
            )
        if block and block < await contract_creation_block_async(self.factory):
            if debug_logs:
                log_debug(
                    "block %s is before %s deploy block",
                    block,
                    await contract_creation_block_async(self.factory),
                )
            return 0
        if self._supports_factory_helper and (
            block is None or block >= await contract_creation_block_async(FACTORY_HELPER)
        ):
            try:
                deepest_pool, liquidity = await self.deepest_pool_for(
                    token, block, ignore_pools=ignore_pools
                )
                await log_liquidity(self, token, block, liquidity, debug_logs)
                return liquidity
            except (Revert, ValueError, ContractLogicError) as e:
                _log_factory_helper_failure(e, token, block, ignore_pools)

        pools = self.pools_for_token(token, block=block, _ignore_pools=ignore_pools)
        try:
            liquidity = await UniswapV2Pool.check_liquidity.max(
                pools, token=token, block=block, sync=False
            )
        except a_sync.exceptions.EmptySequenceError:
            liquidity = 0
        await log_liquidity(self, token, block, liquidity, debug_logs)
        return liquidity

    @a_sync.a_sync(ram_cache_maxsize=100_000, ram_cache_ttl=60 * 60)
    @stuck_coro_debugger
    async def deepest_pool_for(
        self, token: Address, block: Block = None, *, ignore_pools=[]
    ) -> Tuple[Address, int]:
        # sourcery skip: default-mutable-arg
        with reraise_excs_with_extra_context(self, token, block, ignore_pools):
            deepest = await FACTORY_HELPER.deepestPoolFor.coroutine(
                self.factory, token, ignore_pools, block_identifier=block
            )
            logger.debug("got deepest pool for %s at %s: %s from helper", token, block, deepest)
            return deepest

    def _smol_brain_path_selector(
        self,
        token_in: AddressOrContract,
        token_out: AddressOrContract,
        paired_against: AddressOrContract,
    ) -> Path:
        # sourcery skip: assign-if-exp, lift-return-into-if, merge-duplicate-blocks, merge-else-if-into-elif, remove-redundant-if, remove-unnecessary-cast
        """Chooses swap path to use for quote"""
        # NOTE: can we just delete this now? probably, must test
        token_in, token_out, paired_against = (
            str(token_in),
            str(token_out),
            str(paired_against),
        )

        if str(paired_against) in STABLECOINS and str(token_out) in STABLECOINS:
            path = [token_in, paired_against]
        elif weth in (token_in, token_out):
            path = [token_in, token_out]
        elif sushi and paired_against == sushi and token_out != sushi:
            path = [token_in, sushi, weth, token_out]
        elif str(token_in) in self.special_paths and str(token_out) in STABLECOINS:
            path = self.special_paths[str(token_in)]

        elif CHAINID == Network.BinanceSmartChain:
            from y.constants import cake, wbnb

            if WRAPPED_GAS_COIN in (token_in, token_out):
                path = [token_in, token_out]
            elif cake.address in (token_in, token_out):
                path = [token_in, token_out]
            else:
                path = [token_in, wbnb.address, token_out]
        else:
            if WRAPPED_GAS_COIN in (token_in, token_out):
                path = [token_in, token_out]
            else:
                path = [token_in, WRAPPED_GAS_COIN, token_out]

        return path


def log_debug(msg: str, *args: Any):
    __log(DEBUG, msg, args)


__log = logger._log


async def log_liquidity(market, token, block, liquidity, debug_logs: bool = True):
    if debug_logs:
        __log(
            DEBUG,
            "%s liquidity for %s %s at %s is %s",
            (
                repr(market),
                await ERC20(token, asynchronous=True).symbol,
                token,
                block,
                liquidity,
            ),
        )
