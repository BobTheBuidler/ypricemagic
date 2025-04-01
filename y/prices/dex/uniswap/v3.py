import math
from collections import defaultdict
from decimal import Decimal
from functools import cached_property, lru_cache
from itertools import cycle, islice
from logging import DEBUG, getLogger
from typing import (
    AsyncIterator,
    DefaultDict,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
)

import a_sync
import eth_retry
from a_sync import igather
from a_sync.a_sync import HiddenMethodDescriptor
from brownie.network.event import _EventItem
from eth_typing import ChecksumAddress, HexAddress
from typing_extensions import Self

from y import convert
from y import ENVIRONMENT_VARIABLES as ENVS
from y._decorators import stuck_coro_debugger
from y.classes.common import ERC20, ContractBase
from y.constants import CHAINID, CONNECTED_TO_MAINNET, usdc, weth
from y.contracts import Contract, contract_creation_block_async
from y.datatypes import Address, AnyAddressType, Block, Pool, UsdPrice
from y.exceptions import (
    ContractNotVerified,
    TokenNotFound,
    call_reverted,
)
from y.interfaces.uniswap.quoterv3 import UNIV3_QUOTER_ABI
from y.networks import Network
from y.utils.events import ProcessedEvents

try:
    from eth_abi.packed import encode_packed
except ImportError:
    from eth_abi.packed import encode_abi_packed as encode_packed

# https://github.com/Uniswap/uniswap-v3-periphery/blob/main/deploys.md
UNISWAP_V3_FACTORY = "0x1F98431c8aD98523631AE4a59f267346ea31F984"
UNISWAP_V3_QUOTER = "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6"

logger = getLogger(__name__)

Path = Iterable[Union[Address, int]]

# same addresses on all networks
addresses = {
    Network.Mainnet: {
        "factory": UNISWAP_V3_FACTORY,
        "quoter": UNISWAP_V3_QUOTER,
        "fee_tiers": (3000, 500, 10_000, 100),
    },
    Network.Arbitrum: {
        "factory": UNISWAP_V3_FACTORY,
        "quoter": UNISWAP_V3_QUOTER,
        "fee_tiers": (3000, 500, 10_000),
    },
    Network.Optimism: {
        "factory": UNISWAP_V3_FACTORY,
        "quoter": UNISWAP_V3_QUOTER,
        "fee_tiers": (3000, 500, 10_000, 100),
    },
    Network.Base: {
        "factory": "0x33128a8fC17869897dcE68Ed026d694621f6FDfD",
        "quoter": "0x3d4e44Eb1374240CE5F1B871ab261CD16335B76a",  # quoter v2
        "fee_tiers": (3000, 500, 10_000, 100),
    },
}

forked_deployments = {
    Network.Optimism: [
        {
            # Velodrome slipstream
            "factory": "0xCc0bDDB707055e04e497aB22a59c2aF4391cd12F",
            "quoter": "0x89D8218ed5fF1e46d8dcd33fb0bbeE3be1621466",
            "fee_tiers": (3000, 500, 10_000, 100),
        }
    ],
    Network.Base: [
        {
            # Aerodrome slipstream
            "factory": "0x5e7BB104d84c7CB9B682AaC2F3d509f5F406809A",
            "quoter": "0x254cF9E1E6e233aa1AC962CB9B05b2cfeAaE15b0",
            "fee_tiers": (3000, 500, 10_000, 100),
        },
    ],
}

_FEE_DENOMINATOR = Decimal(1_000_000)

_PATH_TYPE_STRINGS: Dict[int, Tuple[Literal["address", "uint24"], ...]] = {
    3: tuple(islice(cycle(("address", "uint24")), 3)),
    5: tuple(islice(cycle(("address", "uint24")), 5)),
}


class UniswapV3Pool(ContractBase):
    """Represents a Uniswap V3 Pool."""

    __contains_cache__: Dict[Address, Dict[ChecksumAddress, bool]] = {}

    __slots__ = "fee", "token0", "token1", "tick_spacing"

    def __init__(
        self,
        address: Address,
        token0: Address,
        token1: Address,
        tick_spacing: int,
        fee: int,
        deploy_block: int,
        asynchronous: bool = False,
    ) -> None:
        """
        Initialize a UniswapV3Pool instance.

        Args:
            address: The address of the pool.
            token0: The address of the first token in the pool.
            token1: The address of the second token in the pool.
            tick_spacing: The tick spacing of the pool.
            fee: The fee of the pool.
            deploy_block: The block number when the pool was deployed.
            asynchronous: Whether to use asynchronous operations.

        Examples:
            >>> pool = UniswapV3Pool(
            ...     address="0x1234567890abcdef1234567890abcdef12345678",
            ...     token0="0xToken0Address",
            ...     token1="0xToken1Address",
            ...     tick_spacing=60,
            ...     fee=3000,
            ...     deploy_block=1234567,
            ...     asynchronous=True
            ... )
        """
        super().__init__(address, asynchronous=asynchronous)
        self.token0 = ERC20(token0, asynchronous=asynchronous)
        self.token1 = ERC20(token1, asynchronous=asynchronous)
        self.tick_spacing = tick_spacing
        self.fee = fee
        self._deploy_block = deploy_block

    def __contains__(self, token: Address) -> bool:
        """
        Check if a token is part of the pool.

        Args:
            token: The address of the token to check.

        Returns:
            True if the token is part of the pool, False otherwise.

        Examples:
            >>> pool = UniswapV3Pool(...)
            >>> "0xToken0Address" in pool
            True
        """
        # force token to string in case it is Contract or EthAddress etc
        token = str(token)
        cache_for_token = self.__contains_cache__.get(token, {})
        cache_value = cache_for_token.get(self.address)
        if cache_value is None:
            if not cache_for_token:
                self.__contains_cache__[token] = {}
            cache_value = token in (self.token0.address, self.token1.address)
            self.__contains_cache__[token][self.address] = cache_value
        return cache_value

    def __getitem__(self, token: Address) -> ERC20:
        """
        Get the ERC20 token object for a given token address.

        Args:
            token: The address of the token.

        Returns:
            The ERC20 token object.

        Raises:
            TokenNotFound: If the token is not part of the pool.

        Examples:
            >>> pool = UniswapV3Pool(...)
            >>> token = pool["0xToken0Address"]
        """
        if token not in self:
            raise TokenNotFound(token, self)
        return ERC20(token, asynchronous=self.asynchronous)

    # DEBUG: lets try a semaphore here
    @a_sync.a_sync(ram_cache_maxsize=100_000, ram_cache_ttl=60 * 60, semaphore=10000)
    async def check_liquidity(
        self, token: AnyAddressType, block: Block
    ) -> Optional[int]:
        """
        Check the liquidity of a token in the pool at a specific block.

        Args:
            token: The address of the token.
            block: The block number to check liquidity at.

        Returns:
            The liquidity of the token in the pool, or None if not available.

        Examples:
            >>> pool = UniswapV3Pool(...)
            >>> liquidity = await pool.check_liquidity("0xToken0Address", 1234567)
        """
        if debug_logs_enabled := logger.isEnabledFor(DEBUG):
            logger._log(
                DEBUG,
                "checking %s liquidity for %s %s at %s",
                (
                    repr(self),
                    await ERC20(token, asynchronous=True).symbol,
                    token,
                    block,
                ),
            )

        if block < await self.deploy_block(sync=False):
            if debug_logs_enabled:
                logger._log(
                    DEBUG, "block %s prior to %s deploy block", (block, repr(self))
                )
            return 0

        try:
            liquidity = await self[token].balance_of(self.address, block, sync=False)
        except ContractNotVerified:
            if debug_logs_enabled:
                logger._log(
                    DEBUG,
                    "%s is not verified and we cannot fetch balance the usual way. returning 0.",
                    (token,),
                )
            return 0

        if debug_logs_enabled:
            await log_liquidity(self, token, block, liquidity)
        return liquidity

    @a_sync.a_sync(ram_cache_maxsize=100_000, ram_cache_ttl=60 * 60)
    async def _check_liquidity_token_out(
        self, token_in: AnyAddressType, block: Block
    ) -> Optional[int]:
        """
        Check the liquidity of the token out for a given token in.

        Args:
            token_in: The address of the token in.
            block: The block number to check liquidity at.

        Returns:
            The liquidity of the token out, or None if not available.

        Examples:
            >>> pool = UniswapV3Pool(...)
            >>> liquidity = await pool._check_liquidity_token_out("0xToken0Address", 1234567)
        """
        return await self.check_liquidity(
            self._get_token_out(token_in), block=block, sync=False
        )

    @lru_cache
    def _get_token_out(self, token_in: ERC20) -> ERC20:
        """
        Get the token out for a given token in.

        Args:
            token_in: The ERC20 token object for the token in.

        Returns:
            The ERC20 token object for the token out.

        Raises:
            TokenNotFound: If the token in is not part of the pool.

        Examples:
            >>> pool = UniswapV3Pool(...)
            >>> token_out = pool._get_token_out(token_in)
        """
        if token_in == self.token0:
            return self.token1
        elif token_in == self.token1:
            return self.token0
        raise TokenNotFound(token_in, self)


class UniswapV3(a_sync.ASyncGenericBase):
    """Represents the Uniswap V3 protocol."""

    def __init__(
        self,
        factory: HexAddress,
        quoter: HexAddress,
        fee_tiers: List[int],
        asynchronous: bool = True,
    ) -> None:
        """
        Initialize a UniswapV3 instance.

        Args:
            asynchronous: Whether to use asynchronous operations.

        Raises:
            UnsupportedNetwork: If Uniswap V3 is not supported on the current network.

        Examples:
            >>> uniswap_v3 = UniswapV3(asynchronous=True)
        """
        super().__init__()
        self.asynchronous = asynchronous
        self._factory = convert.to_address(factory)
        self._quoter = convert.to_address(quoter)
        self.fee_tiers = fee_tiers
        self.loading = False
        self._pools = {}

    def __repr__(self) -> str:
        return f"<{type(self).__name__} factory={self._factory} quoter={self._quoter}>"

    def __contains__(self, asset) -> bool:
        """
        Check if an asset is part of the Uniswap V3 protocol.

        Args:
            asset: The asset to check.

        Returns:
            True if the asset is part of the protocol, False otherwise.

        Examples:
            >>> uniswap_v3 = UniswapV3(...)
            >>> "0xAssetAddress" in uniswap_v3
            True
        """
        return CHAINID in addresses

    @cached_property
    def loaded(self) -> a_sync.Event:
        """
        Get the loaded event for the Uniswap V3 instance.

        Returns:
            The loaded event.

        Examples:
            >>> uniswap_v3 = UniswapV3(...)
            >>> loaded_event = uniswap_v3.loaded
        """
        return a_sync.Event(name=str(self))

    @a_sync.aka.property
    async def factory(self) -> Contract:
        """
        Get the factory contract for the Uniswap V3 protocol.

        Returns:
            The factory contract.

        Examples:
            >>> uniswap_v3 = UniswapV3(...)
            >>> factory_contract = await uniswap_v3.factory
        """
        return await Contract.coroutine(self._factory)

    __factory__: HiddenMethodDescriptor[Self, Contract]

    @a_sync.aka.cached_property
    async def quoter(self) -> Contract:
        """
        Get the quoter contract for the Uniswap V3 protocol.

        Returns:
            The quoter contract.

        Examples:
            >>> uniswap_v3 = UniswapV3(...)
            >>> quoter_contract = await uniswap_v3.quoter
        """
        try:
            return await Contract.coroutine(self._quoter)
        except ContractNotVerified:
            return Contract.from_abi("Quoter", self._quoter, UNIV3_QUOTER_ABI)

    __quoter__: HiddenMethodDescriptor[Self, Contract]

    @a_sync.aka.cached_property
    @stuck_coro_debugger
    async def pools(self) -> List[UniswapV3Pool]:
        """
        Get the list of Uniswap V3 pools.

        Returns:
            A list of Uniswap V3 pools.

        Examples:
            >>> uniswap_v3 = UniswapV3(...)
            >>> pools = await uniswap_v3.pools
        """
        factory = await self.__factory__
        if (
            CHAINID == Network.Base
            and factory.address == "0x5e7BB104d84c7CB9B682AaC2F3d509f5F406809A"
        ):
            return SlipstreamPools(factory, asynchronous=self.asynchronous)
        elif (
            CHAINID == Network.Optimism
            and factory.address == "0xCc0bDDB707055e04e497aB22a59c2aF4391cd12F"
        ):
            return SlipstreamPools(factory, asynchronous=self.asynchronous)
        return UniV3Pools(factory, asynchronous=self.asynchronous)

    __pools__: HiddenMethodDescriptor[Self, "UniV3Pools"]

    async def pools_for_token(
        self, token: Address, block: Block
    ) -> AsyncIterator[UniswapV3Pool]:
        """
        Get the pools for a specific token.

        Args:
            token: The address of the token.
            block: The block number to get pools at.

        Yields:
            Uniswap V3 pools for the token.

        Examples:
            >>> uniswap_v3 = UniswapV3(...)
            >>> async for pool in uniswap_v3.pools_for_token("0xTokenAddress", 1234567):
            ...     print(pool)
        """
        pools = await self.__pools__
        async for pool in pools.objects(to_block=block):
            if token in pool:
                yield pool

    @stuck_coro_debugger
    @a_sync.a_sync(cache_type="memory", ram_cache_ttl=ENVS.CACHE_TTL)
    async def get_price(
        self,
        token: Address,
        block: Optional[Block] = None,
        ignore_pools: Tuple[Pool, ...] = (),  # unused
        skip_cache: bool = ENVS.SKIP_CACHE,  # unused
    ) -> Optional[UsdPrice]:
        """
        Get the price of a token in USD.

        Args:
            token: The address of the token.
            block: The block number to get the price at.
            ignore_pools: Pools to ignore (unused).
            skip_cache: Whether to skip cache (unused).

        Returns:
            The price of the token in USD, or None if not available.

        Examples:
            >>> uniswap_v3 = UniswapV3(...)
            >>> price = await uniswap_v3.get_price("0xTokenAddress", 1234567)
        """
        quoter = await self.__quoter__
        if block and block < await contract_creation_block_async(quoter, True):
            return None

        paths: List[Path] = [(token, fee, usdc.address) for fee in self.fee_tiers]
        if token != weth:
            paths += [
                (token, fee, weth.address, self.fee_tiers[0], usdc.address)
                for fee in self.fee_tiers
            ]

        if debug_logs_enabled := logger.isEnabledFor(DEBUG):
            logger._log(DEBUG, "paths: %s", (paths,))

        amount_in = await ERC20._get_scale_for(token)
        results = await igather(
            self._quote_exact_input(path, amount_in, block) for path in paths
        )

        if debug_logs_enabled:
            logger._log(DEBUG, "results: %s", (results,))

        outputs = list(filter(None, results))
        if debug_logs_enabled:
            logger._log(DEBUG, "outputs: %s", (outputs,))
        return UsdPrice(max(outputs)) if outputs else None

    @stuck_coro_debugger
    @a_sync.a_sync(ram_cache_maxsize=100_000, ram_cache_ttl=60 * 60)
    async def check_liquidity(
        self, token: Address, block: Block, ignore_pools: Tuple[Pool, ...] = ()
    ) -> int:
        """
        Check the liquidity of a token in the Uniswap V3 protocol.

        Args:
            token: The address of the token.
            block: The block number to check liquidity at.
            ignore_pools: Pools to ignore.

        Returns:
            The liquidity of the token.

        Examples:
            >>> uniswap_v3 = UniswapV3(...)
            >>> liquidity = await uniswap_v3.check_liquidity("0xTokenAddress", 1234567)
        """
        if debug_logs_enabled := logger.isEnabledFor(DEBUG):
            logger._log(
                DEBUG,
                "checking %s liquidity for %s %s at %s",
                (self, await ERC20(token, asynchronous=True).symbol, token, block),
            )

        if (
            CONNECTED_TO_MAINNET
            and token == "0x6DEA81C8171D0bA574754EF6F8b412F2Ed88c54D"
        ):
            # LQTY, TODO refactor this somehow
            return 0

        quoter = await self.__quoter__
        if block and block < await contract_creation_block_async(quoter):
            if debug_logs_enabled:
                logger._log(
                    DEBUG, "block %s is before %s deploy block", (block, quoter)
                )
            return 0

        if token == weth.address:
            # NOTE: we need to filter these or else we will be fetching every pool
            #       for now, we only focus on weth/usdc pools
            filter_fn = (
                lambda pool: pool._get_token_out(token) == usdc.address
                and pool not in ignore_pools
            )
        else:
            filter_fn = lambda pool: pool not in ignore_pools

        token_out_tasks = UniswapV3Pool._check_liquidity_token_out.map(
            token_in=token, block=block
        )
        pools_for_token: a_sync.ASyncIterator[UniswapV3Pool] = self.pools_for_token(
            token, block
        )

        if debug_logs_enabled:
            async for pool in pools_for_token.filter(filter_fn):
                # the mapping will start the tasks internally
                logger._log(DEBUG, "starting token_out_task for %s", (pool,))
                token_out_tasks[pool]
        else:
            async for pool in pools_for_token.filter(filter_fn):
                token_out_tasks[pool]

        if not token_out_tasks:
            return 0

        if debug_logs_enabled:
            logger._log(
                DEBUG,
                "%s token_out_tasks for %s at %s: %s",
                (self, token, block, token_out_tasks),
            )

        # Since uni v3 liquidity can be provided asymmetrically, the most liquid pool in terms of `token` might not actually be the most liquid pool in terms of `token_out`
        # We need some spaghetticode here to account for these erroneous liquidity values
        # TODO: Refactor this
        token_out_liquidity: DefaultDict[ERC20, List[int]] = defaultdict(list)
        if debug_logs_enabled:
            async for pool, liquidity in token_out_tasks.map(pop=False):
                await log_liquidity(pool, token, block, liquidity)
                token_out_liquidity[pool._get_token_out(token)].append(liquidity)
            logger._log(
                DEBUG, "%s token_out_liquidity: %s", (token, token_out_liquidity)
            )
        else:
            async for pool, liquidity in token_out_tasks.map(pop=False):
                token_out_liquidity[pool._get_token_out(token)].append(liquidity)

        token_out_min_liquidity = {
            token_out: min(liquidities)
            for token_out, liquidities in token_out_liquidity.items()
        }

        token_in_tasks = UniswapV3Pool.check_liquidity.map(token=token, block=block)
        async for pool, liquidity in token_out_tasks.map(pop=True):
            token_out = pool._get_token_out(token)
            if (
                len(token_out_liquidity[token_out]) > 1
                and liquidity == token_out_min_liquidity[token_out]
            ):
                if debug_logs_enabled:
                    logger._log(DEBUG, "ignoring liquidity for %s", (pool,))
            elif token_out == weth and liquidity < 10**19:  # 10 ETH
                # NOTE: this is totally arbitrary, works for all known cases but eventually will probably cause issues
                if debug_logs_enabled:
                    logger._log(DEBUG, "insufficient liquidity for %s", (pool,))
            else:
                token_in_tasks[pool]

        liquidity = (
            await token_in_tasks.max(pop=True, sync=False) if token_in_tasks else 0
        )
        if debug_logs_enabled:
            await log_liquidity(self, token, block, liquidity)
        return liquidity

    @stuck_coro_debugger
    @eth_retry.auto_retry
    async def _quote_exact_input(
        self, path: Path, amount_in: int, block: int
    ) -> Optional[Decimal]:
        """
        Quote the exact input for a given path and amount.

        Args:
            path: The path for the swap.
            amount_in: The input amount.
            block: The block number to quote at.

        Returns:
            The quoted output amount.

        Examples:
            >>> uniswap_v3 = UniswapV3(...)
            >>> output_amount = await uniswap_v3._quote_exact_input(path, 1000, 1234567)
        """
        quoter = await self.__quoter__
        try:
            amount = await quoter.quoteExactInput.coroutine(
                _encode_path(path), amount_in, block_identifier=block
            )
            return (
                # Quoter v2 uses this weird return struct, we must unpack it to get amount out.
                (amount if isinstance(amount, int) else amount[0])
                / _undo_fees(path)
                / _FEE_DENOMINATOR
            )
        except Exception as e:
            if not call_reverted(e):
                raise


def _encode_path(path: Path) -> bytes:
    """
    Encode a path for Uniswap V3.

    Args:
        path: The path to encode.

    Returns:
        The encoded path.

    Examples:
        >>> path = ["0xToken0Address", 3000, "0xToken1Address"]
        >>> encoded_path = _encode_path(path)
    """
    return encode_packed(_PATH_TYPE_STRINGS[len(path)], path)


def _undo_fees(path: Path) -> Decimal:
    """
    Undo the fees for a given path.

    Args:
        path: The path to undo fees for.

    Returns:
        The fee multiplier.

    Examples:
        >>> path = ["0xToken0Address", 3000, "0xToken1Address"]
        >>> fee_multiplier = _undo_fees(path)
    """
    fees = (1 - fee / _FEE_DENOMINATOR for fee in islice(path, 1, None, 2))
    return math.prod(fees)


class UniV3Pools(ProcessedEvents[UniswapV3Pool]):
    """Represents a collection of Uniswap V3 Pools."""

    __slots__ = ("asynchronous",)

    def __init__(self, factory: Contract, asynchronous: bool = False):
        """
        Initialize a UniV3Pools instance.

        Args:
            factory: The factory contract for Uniswap V3.
            asynchronous: Whether to use asynchronous operations.

        Examples:
            >>> factory_contract = Contract(...)
            >>> pools = UniV3Pools(factory_contract, asynchronous=True)
        """
        self.asynchronous = asynchronous
        super().__init__(
            addresses=[factory.address], topics=[factory.topics["PoolCreated"]]
        )

    def _process_event(self, event: _EventItem) -> UniswapV3Pool:
        """
        Process a PoolCreated event and return a UniswapV3Pool instance.

        Args:
            event: The PoolCreated event.

        Returns:
            A UniswapV3Pool instance.

        Examples:
            >>> pools = UniV3Pools(...)
            >>> pool = pools._process_event(event)
        """
        token0, token1, fee, tick_spacing, pool = event.values()
        return UniswapV3Pool(
            pool,
            token0,
            token1,
            fee,
            tick_spacing,
            event.block_number,
            asynchronous=self.asynchronous,
        )

    def _get_block_for_obj(self, obj: UniswapV3Pool) -> int:
        """
        Get the block number for a UniswapV3Pool object.

        Args:
            obj: The UniswapV3Pool object.

        Returns:
            The block number.

        Examples:
            >>> pools = UniV3Pools(...)
            >>> block_number = pools._get_block_for_obj(pool)
        """
        return obj._deploy_block


class SlipstreamPools(UniV3Pools):
    def _process_event(self, event: _EventItem) -> UniswapV3Pool:
        token0, token1, tick_spacing, pool = event.values()
        return UniswapV3Pool(
            pool,
            token0,
            token1,
            # NOTE: fee arg is not actually used in the current implementation, so we can use 0 here
            0,  # TODO: implement fee maths properly
            tick_spacing,
            event.block_number,
            asynchronous=self.asynchronous,
        )


if CHAINID in addresses:
    uniswap_v3 = UniswapV3(
        addresses[CHAINID]["factory"],
        addresses[CHAINID]["quoter"],
        addresses[CHAINID]["fee_tiers"],
        asynchronous=True,
    )
else:
    uniswap_v3 = None

forks = [
    UniswapV3(fork["factory"], fork["quoter"], fork["fee_tiers"], asynchronous=True)
    for fork in forked_deployments.get(CHAINID, [])
]


async def log_liquidity(market, token, block, liquidity) -> None:
    __logger_log(
        DEBUG,
        "%s liquidity for %s %s at %s: %s",
        (
            repr(market),
            await ERC20(token, asynchronous=True).symbol,
            token,
            block,
            liquidity,
        ),
    )


__logger_log = logger._log
