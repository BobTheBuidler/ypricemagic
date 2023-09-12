import asyncio
import logging
from typing import Awaitable, Dict, List, NewType, Optional, Tuple

import a_sync
from brownie import chain
from brownie.convert.datatypes import EthAddress
from hexbytes import HexBytes
from multicall import Call

from y import ENVIRONMENT_VARIABLES as ENVS
from y import constants, contracts
from y.classes.common import ERC20, ContractBase, WeiBalance
from y.datatypes import Address, AnyAddressType, Block, UsdPrice, UsdValue
from y.networks import Network
from y.utils.events import decode_logs, get_logs_asap
from y.utils.logging import get_price_logger
from y.utils.raw_calls import raw_call

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

class BalancerV2Vault(ContractBase):
    def __init__(self, address: AnyAddressType, asynchronous: bool = False) -> None:
        super().__init__(address, asynchronous=asynchronous)
        if not self._is_cached:
            # we need the contract cached so we can decode logs correctly
            self.contract
            
    @a_sync.a_sync(ram_cache_ttl=ENVS.CACHE_TTL)
    async def get_pool_tokens(self, pool_id: int, block: Optional[Block] = None):
        return await self.contract.getPoolTokens.coroutine(pool_id, block_identifier = block)
    
    @a_sync.a_sync(ram_cache_ttl=ENVS.CACHE_TTL)
    async def list_pools(self, block: Optional[Block] = None) -> Dict[HexBytes,EthAddress]:
        topics = ['0x3c13bc30b8e878c53fd2a36b679409c073afd75950be43d8858768e956fbc20e']
        events = decode_logs(await get_logs_asap(self.address, topics, to_block=block, sync=False))
        return {
            event['poolId'].hex(): event['poolAddress'] for event in events
            # NOTE: For some reason the Balancer fork on Fantom lists "0x3e522051A9B1958Aa1e828AC24Afba4a551DF37d"
            #       as a pool, but it is not a contract. This handler will prevent it and future cases from causing problems.
            if contracts.is_contract(event['poolAddress'])
        }
    
    @a_sync.a_sync(ram_cache_ttl=ENVS.CACHE_TTL)
    async def get_pool_info(self, poolids: Tuple[HexBytes,...], block: Optional[Block] = None) -> List[Tuple]:
        return await asyncio.gather(*[
            self.contract.getPoolTokens.coroutine(poolId, block_identifier=block)
            for poolId in poolids
        ])
    
    async def deepest_pool_for(self, token_address: Address, block: Optional[Block] = None) -> Tuple[Optional[EthAddress],int]:
        # sourcery skip: simplify-len-comparison
        pools = await self.list_pools(block=block, sync=False)
        poolids = tuple(pools.keys())
        pools_info = await self.get_pool_info(poolids, block=block, sync=False)
        all_pools = await self.list_pools(block=block, sync=False)
        pools_info = {all_pools[poolid]: info for poolid, info in zip(poolids, pools_info) if str(info) != "((), (), 0)"}
        
        logger = get_price_logger(token_address, block, 'balancer.v2')
        deepest_pool = {'pool': None, 'balance': 0}
        for pool, info in pools_info.items():
            num_tokens = len(info[0])
            pool_balances = {info[0][i]: info[1][i] for i in range(num_tokens)}
            pool_balance = [balance for token, balance in pool_balances.items() if token == token_address]
            if len(pool_balance) == 0:
                continue
            assert len(pool_balance) == 1
            pool_balance = pool_balance[0]
            if pool_balance > deepest_pool['balance']:
                deepest_pool = {'pool': pool, 'balance': pool_balance}
        logger.debug("deepest pool %s", deepest_pool)
        return tuple(deepest_pool.values())


class BalancerV2Pool(ERC20):
    def __init__(self, pool_address: AnyAddressType, asynchronous: bool = False) -> None:
        super().__init__(pool_address, asynchronous=asynchronous)

    @a_sync.aka.cached_property
    async def id(self) -> PoolId:
        return PoolId(await Call(self.address, ['getPoolId()(bytes32)']).coroutine())
    
    @a_sync.aka.cached_property
    async def vault(self) -> BalancerV2Vault:
        vault = await raw_call(self.address,'getVault()',output='address', sync=False)
        return BalancerV2Vault(vault, asynchronous=True)
    
    async def get_pool_price(self, block: Optional[Block] = None) -> Awaitable[UsdPrice]:
        tvl, total_supply = await asyncio.gather(
            self.get_tvl(block=block, sync=False),
            self.total_supply_readable(block=block, sync=False),
        )
        return UsdPrice(tvl / total_supply)
        
    async def get_tvl(self, block: Optional[Block] = None) -> Awaitable[UsdValue]:
        balances = await self.get_balances(block=block, sync=False)
        return UsdValue(sum(await asyncio.gather(*[
            balance.__value_usd__(sync=False) for balance in balances.values()
            if balance.token.address != self.address  # NOTE: to prevent an infinite loop for tokens that include themselves in the pool (e.g. bb-a-USDC)
        ])))

    @a_sync.a_sync(ram_cache_ttl=ENVS.CACHE_TTL)
    async def get_balances(self, block: Optional[Block] = None) -> Dict[ERC20, WeiBalance]:
        tokens = await self.tokens(block=block, sync=False)
        return dict(tokens.items())

    async def get_token_price(self, token_address: AnyAddressType, block: Optional[Block] = None) -> Optional[UsdPrice]:
        token_balances, weights = await asyncio.gather(
            self.get_balances(block=block, sync=False),
            self.weights(block=block, sync=False),
        )
        pool_token_info = list(zip(token_balances.keys(),token_balances.values(), weights))
        for pool_token, balance, weight in pool_token_info:
            if pool_token == token_address:
                token_balance, token_weight = balance, weight

        paired_token_balance = None
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

        token_value_in_pool, token_balance_readable = await asyncio.gather(*[
            paired_token_balance.__value_usd__(sync=False),
            token_balance.__readable__(sync=False),
        ])
        token_value_in_pool /= paired_token_weight * token_weight
        return UsdPrice(token_value_in_pool / token_balance_readable) 

    # NOTE: We can't cache this as a cached property because some balancer pool tokens can change. Womp
    @a_sync.a_sync(ram_cache_ttl=ENVS.CACHE_TTL)
    async def tokens(self, block: Optional[Block] = None) -> Dict[ERC20, WeiBalance]:
        vault, id = await asyncio.gather(self.__vault__(sync=False), self.__id__(sync=False))
        tokens, balances, lastChangedBlock = await vault.get_pool_tokens(id, block=block, sync=False)
        return {ERC20(token, asynchronous=self.asynchronous): WeiBalance(balance, token, block=block) for token, balance in zip(tokens, balances)}

    @a_sync.a_sync(ram_cache_ttl=ENVS.CACHE_TTL)
    async def weights(self, block: Optional[Block] = None) -> List[int]:
        try:
            return await self.contract.getNormalizedWeights.coroutine(block_identifier = block)
        except (AttributeError,ValueError):
            tokens = await self.tokens(block=block, sync=False)
            return [1 for _ in tokens.keys()]


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

    async def is_pool(self, token_address: AnyAddressType) -> bool:
        methods = ('getPoolId()(bytes32)','getPausedState()((bool,uint,uint))','getSwapFeePercentage()(uint)')
        return await contracts.has_methods(token_address, methods, sync=False)
    
    async def get_pool_price(self, pool_address: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
        return await BalancerV2Pool(pool_address, asynchronous=True).get_pool_price(block=block)

    async def get_token_price(self, token_address: Address, block: Optional[Block] = None) -> UsdPrice:
        deepest_pool: Optional[BalancerV2Pool] = await self.deepest_pool_for(token_address, block=block, sync=False)
        if deepest_pool is None:
            return
        return await deepest_pool.get_token_price(token_address, block, sync=False)
    
    async def deepest_pool_for(self, token_address: Address, block: Optional[Block] = None) -> Optional[BalancerV2Pool]:
        deepest_pools = await asyncio.gather(*[vault.deepest_pool_for(token_address, block=block, sync=False) for vault in self.vaults])
        deepest_pools = {vault.address: deepest_pool for vault, deepest_pool in zip(self.vaults, deepest_pools) if deepest_pool is not None}
        deepest_pool_balance = max(pool_balance for pool_address, pool_balance in deepest_pools.values())
        for pool_address, pool_balance in deepest_pools.values():
            if pool_balance == deepest_pool_balance and pool_address:
                return BalancerV2Pool(pool_address, asynchronous=self.asynchronous)

balancer = BalancerV2(asynchronous=True)
