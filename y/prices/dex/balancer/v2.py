
import asyncio
import logging
from collections import defaultdict
from contextlib import suppress
from enum import IntEnum
from typing import (Any, AsyncIterator, Awaitable, Callable, Dict, List, NewType, 
                    Optional, Tuple, TypeVar, Union)

import a_sync
from a_sync.a_sync import HiddenMethodDescriptor
from brownie import ZERO_ADDRESS, chain
from brownie.convert.datatypes import EthAddress
from brownie.network.contract import ContractCall, ContractTx, OverloadedMethod
from brownie.network.event import _EventItem
from hexbytes import HexBytes
from multicall import Call
from typing_extensions import Self
from web3.exceptions import ContractLogicError

from y import ENVIRONMENT_VARIABLES as ENVS
from y import constants, contracts
from y._decorators import stuck_coro_debugger
from y.classes.common import ERC20, ContractBase, WeiBalance
from y.contracts import Contract
from y.datatypes import Address, AnyAddressType, Block, UsdPrice, UsdValue
from y.exceptions import ContractNotVerified, TokenNotFound
from y.networks import Network
from y.prices.dex.balancer._abc import BalancerABC, BalancerPool
from y.utils.cache import a_sync_ttl_cache
from y.utils.events import ProcessedEvents
from y.utils.logging import get_price_logger


BALANCER_V2_VAULTS = {
    Network.Mainnet: [
        '0xBA12222222228d8Ba445958a75a0704d566BF2C8',
    ],
    Network.Fantom: [
        '0x20dd72Ed959b6147912C2e529F0a0C651c33c9ce',
    ],
    Network.Polygon: [
        '0xBA12222222228d8Ba445958a75a0704d566BF2C8',
    ],
    Network.Arbitrum: [
        '0xBA12222222228d8Ba445958a75a0704d566BF2C8',
    ],
    Network.Base: [
        '0xBA12222222228d8Ba445958a75a0704d566BF2C8',
    ],
}.get(chain.id, [])

MESSED_UP_POOLS = {
    Network.Mainnet: [
        # NOTE: this was the first ever balancer "pool" and isn't actually a pool
        "0xF3799CBAe9c028c1A590F4463dFF039b8F4986BE",
    ],
}.get(chain.id, [])

T = TypeVar("T")

PoolId = NewType('PoolId', bytes)
PoolBalances = Dict[ERC20, WeiBalance]

logger = logging.getLogger(__name__)

class PoolSpecialization(IntEnum):
    ComposableStablePool = 0
    WeightedPool = 1
    WeightedPool2Tokens = 2
    # This is a weird one
    CronV1Pool = -1

    @staticmethod
    def with_immutable_tokens() -> List["PoolSpecialization"]:
        return [
            PoolSpecialization.ComposableStablePool,
            PoolSpecialization.WeightedPool,
            PoolSpecialization.WeightedPool2Tokens,
            PoolSpecialization.CronV1Pool,
        ]


class BalancerV2Vault(ContractBase):
    def __init__(self, address: AnyAddressType, asynchronous: bool = False) -> None:
        super().__init__(address, asynchronous=asynchronous)
        self._events = BalancerEvents(self, addresses=address, topics=['0x3c13bc30b8e878c53fd2a36b679409c073afd75950be43d8858768e956fbc20e'])
        if not self._is_cached:
            # we need the contract cached so we can decode logs correctly
            self.contract
    
    @stuck_coro_debugger
    async def pools(self, block: Optional[Block] = None) -> AsyncIterator["BalancerV2Pool"]:
        async for pool in self._events.events(to_block=block):
            yield pool

    @stuck_coro_debugger
    async def pools_for_token(self, token: Address, block: Optional[Block] = None) -> AsyncIterator["BalancerV2Pool"]:
        async for pool, tokens in BalancerV2Pool.tokens.map(block=block).map(self.pools(block=block), pop=True):
            if token in tokens:
                logger.debug("%s contains %s", pool, token)
                yield pool
                
    @a_sync_ttl_cache
    @stuck_coro_debugger
    async def get_pool_tokens(self, pool_id: HexBytes, block: Optional[Block] = None):
        contract = await contracts.Contract.coroutine(self.address)
        return await contract.getPoolTokens.coroutine(pool_id, block_identifier = block)
    
    @a_sync_ttl_cache
    @stuck_coro_debugger
    async def get_pool_info(self, poolids: Tuple[HexBytes,...], block: Optional[Block] = None) -> List[Tuple]:
        contract = await contracts.Contract.coroutine(self.address)
        return await contract.getPoolTokens.map(poolids, block_identifier=block)
    
    @a_sync_ttl_cache
    @stuck_coro_debugger
    async def deepest_pool_for(self, token_address: Address, block: Optional[Block] = None) -> "BalancerV2Pool":
        balance_tasks: a_sync.TaskMapping[BalancerV2Pool, Optional[WeiBalance]]

        logger = get_price_logger(token_address, block, extra='balancer.v2')

        balance_tasks = BalancerV2Pool.get_balance.map(token_address=token_address, block=block)
        balances_aiterator = balance_tasks.map(self.pools_for_token(token_address, block=block), pop=True)        
        async for pool, balance in balances_aiterator.filter(_lookup_balance_from_tuple).sort(key=_lookup_balance_from_tuple, reverse=True):
            logger.debug("deepest pool %s balance %s", pool, balance)
            return pool

class BalancerEvents(ProcessedEvents[Tuple[HexBytes, EthAddress, Block]]):
    threads = a_sync.PruningThreadPoolExecutor(6)
    __slots__ = "asynchronous", 
    def __init__(self, vault: BalancerV2Vault, *args, asynchronous: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.vault = vault
        self.asynchronous = asynchronous
        self.__tasks = []
    def _include_event(self, event: _EventItem) -> Awaitable[bool]:
        if event['poolAddress'] in MESSED_UP_POOLS:
            return False
        # NOTE: For some reason the Balancer fork on Fantom lists "0x3e522051A9B1958Aa1e828AC24Afba4a551DF37d"
        #       as a pool, but it is not a contract. This handler will prevent it and future cases from causing problems.
        # NOTE: this isn't really optimized as it still runs semi-synchronously but its better than what was had previously
        return self.threads.run(contracts.is_contract, event['poolAddress'])
    def _process_event(self, event: _EventItem) -> "BalancerV2Pool":
        try:
            specialization = PoolSpecialization(event['specialization'])
        except ValueError:
            specialization = None
        pool = BalancerV2Pool(
            address = event['poolAddress'], 
            id = HexBytes(event['poolId']), 
            specialization=specialization,
            vault=self.vault,
            _deploy_block = event.block_number,
            asynchronous = self.asynchronous, 
        )
        # lets get this cached into memory now
        task = asyncio.create_task(pool.tokens(sync=False))
        self.__tasks.append(task)
        task.add_done_callback(self._task_done_callback)
        return pool
    def _get_block_for_obj(self, pool: "BalancerV2Pool") -> int:
        return pool._deploy_block
    def _task_done_callback(self, t: asyncio.Task):
        self.__tasks.remove(t)
        if not t.cancelled():
            # get the exc so it doesn't log, it will come up later
            t.exception()


class BalancerV2Pool(BalancerPool):
    """A pool from Balancer Protocol v2"""
    # internal variables to save calls in some instances
    # they do not necessarily reflect real life at all times
    # defaults are stored as class vars to keep instance dicts smaller
    __nonweighted: bool = False
    __tokens: Tuple[ERC20, ...] = None
    __weights: List[int] = None
    def __init__(
        self, 
        address: AnyAddressType,
        *,
        id: Optional[HexBytes] = None,
        specialization: Optional[PoolSpecialization] = None,
        vault: Optional[BalancerV2Vault] = None,
        asynchronous: bool = False, 
        _deploy_block: Optional[Block] = None,
    ):
        super().__init__(address, asynchronous=asynchronous, _deploy_block=_deploy_block)
        if id is not None:
            self.id = id
        if specialization is not None:
            self.pool_type = specialization
        if vault is not None:
            self.vault = vault

    @a_sync.aka.cached_property
    async def id(self) -> PoolId:
        return await Call(self.address, ['getPoolId()(bytes32)'])
    __id__: HiddenMethodDescriptor[Self, PoolId]
    
    @a_sync.aka.cached_property
    @stuck_coro_debugger
    async def vault(self) -> Optional[BalancerV2Vault]:
        with suppress(ContractLogicError):
            vault = await Call(self.address, ['getVault()(address)'])
            if vault == ZERO_ADDRESS:
                return None
            elif vault:
                return BalancerV2Vault(vault, asynchronous=True)
        # in earlier web3 versions, we would get `None`. More recently, we get ContractLogicError. This handles both
        if chain.id == Network.Mainnet and await self.__build_name__ == "CronV1Pool":
            # NOTE: these `CronV1Pool` tokens ARE balancer pools but don't match the expected pool abi? 
            return BalancerV2Vault("0xBA12222222228d8Ba445958a75a0704d566BF2C8", asynchronous=True)
    __vault__: HiddenMethodDescriptor[Self, Optional[BalancerV2Vault]]

    @a_sync.aka.cached_property
    @stuck_coro_debugger
    async def pool_type(self) -> Union[PoolSpecialization, int]:
        vault = await self.__vault__
        if vault is None:
            raise ValueError(f"{self} has no vault") from None
        elif poolid := await self.__id__:
            _, specialization = await vault.contract.getPool.coroutine(poolid)
        elif chain.id == Network.Mainnet and await self.__build_name__ == "CronV1Pool":
            # NOTE: these `CronV1Pool` tokens ARE balancer pools but don't match the expected pool abi? 
            return PoolSpecialization.CronV1Pool
        else:
            raise ValueError(f"{self} has no poolid") from None
        try:
            return PoolSpecialization(specialization)
        except ValueError:
            if self.address not in _warned:
                with suppress(ContractNotVerified):
                    logger.warning(
                        "ypricemagic does not recognize this pool type, please add `%s = %s` to %s.PoolSpecialization (pool=%s)", 
                        await self.__build_name__, specialization, __name__, self.address
                    )
                _warned.add(self.address)
            return specialization
    __pool_type__: HiddenMethodDescriptor[Self, Optional[PoolSpecialization]]
        
    @stuck_coro_debugger
    async def get_tvl(self, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> Optional[UsdValue]:
        if balances := await self.get_balances(block=block, skip_cache=skip_cache, sync=False):
            # overwrite ref to big obj with ref to little obj
            balances = iter(tuple(balances.values()))
            return UsdValue(await WeiBalance.value_usd.sum(balances, sync=False))

    @a_sync_ttl_cache
    @stuck_coro_debugger
    async def get_balances(self, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> Dict[ERC20, WeiBalance]:
        vault = await self.__vault__
        if vault is None:
            return {}
        tokens, balances, lastChangedBlock = await vault.get_pool_tokens(await self.__id__, block=block, sync=False)
        return {
            ERC20(token, asynchronous=self.asynchronous): WeiBalance(balance, token, block=block, skip_cache=skip_cache)
            for token, balance in zip(tokens, balances)
            # NOTE: some pools include themselves in their own token list, and we should ignore those
            if token != self.address
        }
    
    async def get_balance(self, token_address: Address, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> Optional[WeiBalance]:
        if info := await self.get_balances(block=block, sync=False):
            try:
                return info[token_address]
            except KeyError:
                raise TokenNotFound(token_address, self) from None

    @stuck_coro_debugger
    async def get_token_price(self, token_address: AnyAddressType, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> Optional[UsdPrice]:
        get_balances_coro = self.get_balances(block=block, skip_cache=skip_cache, sync=False)
        if self.__nonweighted:
            # this await will return immediately once cached
            token_balances = await get_balances_coro
            weights = self.__weights
        else:
            token_balances, weights = await asyncio.gather(get_balances_coro, self.weights(block=block, sync=False))
        pool_token_info = list(zip(token_balances.keys(), token_balances.values(), weights))
        for pool_token, token_balance, token_weight in pool_token_info:
            if pool_token == token_address:
                break

        paired_token_balance: Optional[WeiBalance] = None
        for pool_token, balance, weight in pool_token_info:
            if pool_token in constants.STABLECOINS:
                paired_token_balance, paired_token_weight = balance, weight
                break
            elif pool_token == constants.WRAPPED_GAS_COIN:
                paired_token_balance, paired_token_weight = balance, weight
                break
            elif len(pool_token_info) == 2 and pool_token != token_address:
                paired_token_balance, paired_token_weight = balance, weight
                break
        
        if paired_token_balance is None:
            return None

        token_value_in_pool, token_balance_readable = await asyncio.gather(paired_token_balance.__value_usd__, token_balance.__readable__)
        token_value_in_pool /= paired_token_weight * token_weight
        return UsdPrice(token_value_in_pool / token_balance_readable) 

    # NOTE: We can't cache this as a cached property because some balancer pool tokens can change. Womp
    @a_sync_ttl_cache
    @stuck_coro_debugger
    async def tokens(self, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> Tuple[ERC20, ...]:
        if self.__tokens:
            return self.__tokens
        tokens = tuple((await self.get_balances(block=block, skip_cache=skip_cache, sync=False)).keys())
        if await self.__pool_type__ in PoolSpecialization.with_immutable_tokens():
            self.__tokens = tokens
        return tokens

    @a_sync_ttl_cache
    @stuck_coro_debugger
    async def weights(self, block: Optional[Block] = None) -> List[int]:
        contract = await Contract.coroutine(self.address)
        try:
            return await contract.getNormalizedWeights.coroutine(block_identifier = block)
        except AttributeError:
            # Contract has no method `getNormalizedWeights`
            self.__nonweighted = True
            num_tokens = len(await self.tokens(block=block, sync=False))
            self.__weights = [10 ** 18 // num_tokens] * num_tokens
            return self.__weights


class BalancerV2(BalancerABC[BalancerV2Pool]):

    _pool_type = BalancerV2Pool

    _check_methods = ('getPoolId()(bytes32)','getPausedState()((bool,uint,uint))','getSwapFeePercentage()(uint)')

    def __init__(self, asynchronous: bool = False) -> None:
        self.asynchronous = asynchronous
        self.vaults = [BalancerV2Vault(vault, asynchronous=self.asynchronous) for vault in BALANCER_V2_VAULTS]

    @stuck_coro_debugger
    async def get_token_price(self, token_address: Address, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> UsdPrice:
        if deepest_pool := await self.deepest_pool_for(token_address, block=block, sync=False):
            return await deepest_pool.get_token_price(token_address, block, skip_cache=skip_cache, sync=False)
    
    # NOTE: we need a tiny semaphore here because balancer is super arduous and every unpricable token must pass thru this section
    @a_sync.Semaphore(10)
    @stuck_coro_debugger
    async def deepest_pool_for(self, token_address: Address, block: Optional[Block] = None) -> Optional[BalancerV2Pool]:
        kwargs = {"token_address": token_address, "block": block}
        deepest_pools = BalancerV2Vault.deepest_pool_for.map(self.vaults, **kwargs)
        if deepest_pools := {vault.address: deepest_pool async for vault, deepest_pool in deepest_pools if deepest_pool is not None}:
            logger.debug("%s deepest pools for %s at %s: %s", self, token_address, block, deepest_pools)
            async for pool in BalancerV2Pool.get_balance.map(deepest_pools.values(), **kwargs).keys(pop=True).aiterbyvalues(reverse=True):
                return pool
        
        # TODO: afilter
        # deepest_pools = BalancerV2Vault.deepest_pool_for.map(self.vaults, **kwargs).values(pop=True).afilter()
        # async for pool in BalancerV2Pool.get_balance.map(deepest_pools, **kwargs).keys(pop=True).aiterbyvalues(reverse=True):
        #     return pool

balancer = BalancerV2(asynchronous=True)

_lookup_balance_from_tuple: Callable[[Tuple[Any, T]], T] = lambda pool_and_balance: pool_and_balance[1]
"Takes a tuple[K, V] and returns V."

_warned = set()