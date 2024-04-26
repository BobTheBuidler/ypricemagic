
import asyncio
import logging
from collections import defaultdict
from typing import AsyncIterator, Dict, List, NewType, Optional, Tuple

import a_sync
from a_sync.property import HiddenMethodDescriptor
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
from y.classes.common import ERC20, ContractBase, WeiBalance
from y.contracts import Contract
from y.datatypes import Address, AnyAddressType, Block, UsdPrice, UsdValue
from y.decorators import stuck_coro_debugger
from y.networks import Network
from y.utils.cache import a_sync_ttl_cache
from y.utils.events import ProcessedEvents
from y.utils.logging import get_price_logger
from y.utils.raw_calls import raw_call

# TODO: Cache pool tokens for pools that can't change

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


PoolId = NewType('PoolId', bytes)

logger = logging.getLogger(__name__)


class BalancerV2Vault(ContractBase):
    def __init__(self, address: AnyAddressType, asynchronous: bool = False) -> None:
        super().__init__(address, asynchronous=asynchronous)
        self._events = BalancerEvents(addresses=address, topics=['0x3c13bc30b8e878c53fd2a36b679409c073afd75950be43d8858768e956fbc20e'])
        if not self._is_cached:
            # we need the contract cached so we can decode logs correctly
            self.contract
    
    @stuck_coro_debugger
    async def pools(self, block: Optional[Block] = None) -> AsyncIterator["BalancerV2Pool"]:
        async for pool in self._events.events(to_block=block):
            yield pool

    @stuck_coro_debugger
    async def pools_for_token(self, token: Address, block: Optional[Block] = None) -> AsyncIterator["BalancerV2Pool"]:
        async for pool, info in BalancerV2Pool.tokens.map(block=block).map(self.pools(block=block), pop=True):
            if token in info:
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
    async def deepest_pool_for(self, token_address: Address, block: Optional[Block] = None) -> Tuple[Optional["BalancerV2Pool"], int]:
        logger = get_price_logger(token_address, block, 'balancer.v2')
        deepest_pool, deepest_balance = None, 0
        async for pool in self.pools_for_token(token_address, block=block):
            info: Dict[ERC20, WeiBalance]
            if info := await pool.get_balances(block=block, sync=False):
                pool_balance = info[token_address].balance
                if pool_balance > deepest_balance:
                    deepest_pool = pool
        logger.debug("deepest pool %s balance %s", deepest_pool, deepest_balance)
        return deepest_pool, deepest_balance

class BalancerEvents(ProcessedEvents[Tuple[HexBytes, EthAddress, Block]]):
    __slots__ = "asynchronous", 
    def __init__(self, *args, asynchronous: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.asynchronous = asynchronous
    def _include_event(self, event: _EventItem) -> bool:
        # NOTE: For some reason the Balancer fork on Fantom lists "0x3e522051A9B1958Aa1e828AC24Afba4a551DF37d"
        #       as a pool, but it is not a contract. This handler will prevent it and future cases from causing problems.
        return contracts.is_contract(event['poolAddress'])
    def _process_event(self, event: _EventItem) -> "BalancerV2Pool":
        return BalancerV2Pool(event['poolAddress'], asynchronous=self.asynchronous, _deploy_block=event.block_number)
    def _get_block_for_obj(self, pool: "BalancerV2Pool") -> int:
        return pool._deploy_block


MESSED_UP_POOLS = {
    Network.Mainnet: [
        "0xF3799CBAe9c028c1A590F4463dFF039b8F4986BE",
    ],
}.get(chain.id, [])

class BalancerV2Pool(ERC20):
    # defaults are stored as class vars to keep instance dicts smaller
    _messed_up = False
    # internal variables to save calls in some instances
    # they do not necessarily reflect real life at all times
    __nonweighted: bool = False
    __weights: List[int] = None
    __slots__ = "_id", 
    def __init__(
        self, 
        address: AnyAddressType, 
        id: Optional[HexBytes] = None, 
        asynchronous: bool = False, 
        _deploy_block: Optional[Block] = None,
    ):
        super().__init__(address, asynchronous=asynchronous, _deploy_block=_deploy_block)
        self._id = id
        if self.address in MESSED_UP_POOLS:
            self._messed_up = True

    @a_sync.aka.cached_property
    async def id(self) -> PoolId:
        if self._id is None:
            self._id = await Call(self.address, ['getPoolId()(bytes32)'])
        return self._id
    __id__: HiddenMethodDescriptor[Self, PoolId]
    
    @a_sync.aka.cached_property
    async def vault(self) -> Optional[BalancerV2Vault]:
        vault = await raw_call(self.address, 'getVault()', output='address', sync=False)
        return None if vault == ZERO_ADDRESS else BalancerV2Vault(vault, asynchronous=True)
    __vault__: HiddenMethodDescriptor[Self, Optional[BalancerV2Vault]]
    
    @stuck_coro_debugger
    async def get_pool_price(self, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> UsdPrice:
        tvl, total_supply = await asyncio.gather(
            self.get_tvl(block=block, skip_cache=skip_cache, sync=False),
            self.total_supply_readable(block=block, sync=False),
        )
        return UsdPrice(tvl / total_supply)
        
    @stuck_coro_debugger
    async def get_tvl(self, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> Optional[UsdValue]:
        balances: Dict[ERC20, WeiBalance]
        if balances := await self.get_balances(block=block, skip_cache=skip_cache, sync=False):
            return UsdValue(await WeiBalance.value_usd.sum((balance for balance in balances.values() if balance.token.address != self.address), sync=False))

    @a_sync_ttl_cache
    @stuck_coro_debugger
    async def get_balances(self, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> Dict[ERC20, WeiBalance]:
        if self._messed_up:
            return {}
        try:
            vault, id = await asyncio.gather(self.__vault__, self.__id__)
        except ContractLogicError:
            if await self.__build_name__ != "CronV1Pool":
                logger.error("%s is messed up", self)
            return {}
        if vault is None:
            return {}
        tokens, balances, lastChangedBlock = await vault.get_pool_tokens(id, block=block, sync=False)
        return {
            ERC20(token, asynchronous=self.asynchronous): WeiBalance(balance, token, block=block, skip_cache=skip_cache)
            for token, balance in zip(tokens, balances)
        }

    @stuck_coro_debugger
    async def get_token_price(self, token_address: AnyAddressType, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> Optional[UsdPrice]:
        get_balances_coro = self.get_balances(block=block, skip_cache=skip_cache, sync=False)
        if self.__nonweighted:
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
    async def tokens(self, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> Tuple[ERC20]:
        tokens = tuple((await self.get_balances(block=block, skip_cache=skip_cache, sync=False)).keys())
        tokens_history = _tasks_to_help_me_find_pool_types_that_cant_change_tokens[self]
        tokens_history[tokens] += 1
        if len(tokens_history) == 1 and tokens_history[tokens] > 100:
            contract = await contracts.Contract.coroutine(self.address, require_success=False)
            if contract.verified:
                methods = [k for k, v in contract.__dict__.items() if isinstance(v, (ContractCall, ContractTx, OverloadedMethod))]
                logger.debug(
                    "%s has 100 blocks with unchanging list of tokens, contract methods are %s", self, methods)
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

class ImmutableTokensBalancerV2Pool(BalancerV2Pool):
    async def tokens(self, _: Optional[Block] = None) -> List[ERC20]:
        return await self.__tokens
    @a_sync.aka.cached_property
    async def __tokens(self) -> List[ERC20]:
        return await super().tokens()

_tasks_to_help_me_find_pool_types_that_cant_change_tokens = defaultdict(lambda: defaultdict(int))

#yLazyLogger(logger)
@a_sync.a_sync(cache_type='memory')
async def _is_standard_pool(pool: EthAddress) -> bool:
    '''
    Returns `False` if `build_name(pool) in ['ConvergentCurvePool','MetaStablePool']`, else `True`
    '''
    
    # With `return_None_on_failure=True`, if `build_name(pool)` fails,
    # we can't know for sure that its a standard pool, but... it probably is.
    return await contracts.build_name(pool, return_None_on_failure=True, sync=False) not in ['ConvergentCurvePool','MetaStablePool']


class BalancerV2(a_sync.ASyncGenericSingleton):
    def __init__(self, asynchronous: bool = False) -> None:
        self.asynchronous = asynchronous
        self.vaults = [BalancerV2Vault(vault, asynchronous=self.asynchronous) for vault in BALANCER_V2_VAULTS]
    
    def __str__(self) -> str:
        return "BalancerV2()"

    @a_sync.a_sync(ram_cache_ttl=5*60)
    @stuck_coro_debugger
    async def is_pool(self, token_address: AnyAddressType) -> bool:
        methods = ('getPoolId()(bytes32)','getPausedState()((bool,uint,uint))','getSwapFeePercentage()(uint)')
        return await contracts.has_methods(token_address, methods, sync=False)
    
    @stuck_coro_debugger
    async def get_pool_price(self, pool_address: AnyAddressType, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> UsdPrice:
        return await BalancerV2Pool(pool_address, asynchronous=True).get_pool_price(block=block, skip_cache=skip_cache)

    @stuck_coro_debugger
    async def get_token_price(self, token_address: Address, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> UsdPrice:
        deepest_pool: Optional[BalancerV2Pool]
        if deepest_pool := await self.deepest_pool_for(token_address, block=block, sync=False):
            return await deepest_pool.get_token_price(token_address, block, skip_cache=skip_cache, sync=False)
    
    @stuck_coro_debugger
    async def deepest_pool_for(self, token_address: Address, block: Optional[Block] = None) -> Optional[BalancerV2Pool]:
        deepest_pools = BalancerV2Vault.deepest_pool_for.map(self.vaults, token_address=token_address, block=block)
        if deepest_pools := {vault.address: deepest_pool async for vault, deepest_pool in deepest_pools if deepest_pool is not None}:
            deepest_pool_balance = max(dp[1] for dp in deepest_pools.values())
            for pool_address, pool_balance in deepest_pools.values():
                if pool_balance == deepest_pool_balance and pool_address:
                    return BalancerV2Pool(pool_address, asynchronous=self.asynchronous)

balancer = BalancerV2(asynchronous=True)
