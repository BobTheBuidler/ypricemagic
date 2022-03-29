import logging
from functools import cached_property, lru_cache
from typing import Any, Dict, List, Optional, Tuple

from brownie import chain
from brownie.convert.datatypes import EthAddress
from hexbytes import HexBytes
from multicall import Call
from y.classes.common import ERC20, ContractBase, WeiBalance
from y.classes.singleton import Singleton
from y.constants import STABLECOINS, WRAPPED_GAS_COIN
from y.contracts import build_name, has_methods
from y.datatypes import UsdPrice, UsdValue
from y.decorators import log
from y.networks import Network
from y.typing import Address, AnyAddressType, Block
from y.utils.events import decode_logs, get_logs_asap
from y.utils.multicall import fetch_multicall
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)

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
}.get(chain.id, [])


class PoolId(int):
    def __init__(self, v: int) -> None:
        super().__init__()


class BalancerV2Vault(ContractBase):
    def __init__(self, address: AnyAddressType, *args: Any, **kwargs: Any) -> None:
        super().__init__(address, *args, **kwargs)
        if not self._is_cached:
            # we need the contract cached so we can decode logs correctly
            self.contract
    
    @log(logger)
    def get_pool_tokens(self, pool_id: int, block: Optional[Block] = None):
        return self.contract.getPoolTokens(pool_id, block_identifier = block)

    @log(logger)
    @lru_cache(maxsize=10)
    def list_pools(self, block: Optional[Block] = None) -> Dict[HexBytes,EthAddress]:
        topics = ['0x3c13bc30b8e878c53fd2a36b679409c073afd75950be43d8858768e956fbc20e']
        try:
            events = decode_logs(get_logs_asap(self.address, topics, to_block=block))
        except TypeError as e:
            if "Start must be less than or equal to stop" in str(e):
                return {}
            raise
        return {event['poolId'].hex():event['poolAddress'] for event in events}
    
    @lru_cache(maxsize=10)
    def get_pool_info(self, poolids: Tuple[HexBytes,...], block: Optional[Block] = None) -> List[Tuple]:
        return fetch_multicall(*[[self.contract,'getPoolTokens',poolId] for poolId in poolids], block=block)

    @log(logger)
    def deepest_pool_for(self, token_address: Address, block: Optional[Block] = None) -> Tuple[Optional[EthAddress],int]:
        pools = self.list_pools(block=block)
        poolids = (poolid for poolid, pool in pools.items() if _is_standard_pool(pool))
        pools_info = self.get_pool_info(poolids, block=block)
        pools_info = {self.list_pools(block=block)[poolid]: info for poolid, info in zip(poolids, pools_info) if str(info) != "((), (), 0)"}
        
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

        return deepest_pool['pool'], deepest_pool['balance']


class BalancerV2Pool(ERC20):
    def __init__(self, pool_address: AnyAddressType) -> None:
        super().__init__(pool_address)

    @cached_property
    @log(logger)
    def id(self) -> PoolId:
        return Call(self.address, ['getPoolId()(bytes32)'], [['id',PoolId]])()['id']
    
    @cached_property
    @log(logger)
    def vault(self) -> BalancerV2Vault:
        vault = raw_call(self.address,'getVault()',output='address')
        return BalancerV2Vault(vault)

    @log(logger)
    def get_pool_price(self, block: Optional[Block] = None) -> UsdPrice:
        return UsdPrice(self.get_tvl(block=block) / self.total_supply_readable(block=block))

    @log(logger)
    def get_tvl(self, block: Optional[Block] = None) -> UsdValue:
        return UsdValue(
            sum(
                balance.readable * token.price(block=block)
                for token, balance
                in self.get_balances(block=block).items()
            )
        )

    @log(logger)
    def get_balances(self, block: Optional[Block] = None) -> Dict[ERC20, WeiBalance]:
        return {token: balance for token, balance in self.tokens(block=block).items()}

    @log(logger)
    def get_token_price(self, token_address: AnyAddressType, block: Optional[Block] = None) -> Optional[UsdPrice]:
        token_balances = self.get_balances(block=block)
        pool_token_info = list(zip(token_balances.keys(),token_balances.values(), self.weights(block=block)))
        for pool_token, balance, weight in pool_token_info:
            if pool_token == token_address:
                token_balance, token_weight = balance, weight

        for pool_token, balance, weight in pool_token_info:
            if pool_token in STABLECOINS:
                paired_token_balance, paired_token_weight = balance, weight
                break
            elif pool_token == WRAPPED_GAS_COIN:
                paired_token_balance, paired_token_weight = balance, weight
                break
            elif len(pool_token_info) == 2 and pool_token != token_address:
                paired_token_balance, paired_token_weight = balance, weight
                break

        try:
            token_value_in_pool = paired_token_balance.value_usd / paired_token_weight * token_weight
            return UsdPrice(token_value_in_pool / token_balance.readable)
        except UnboundLocalError:
            return None
    
    @log(logger)
    def tokens(self, block: Optional[Block] = None) -> Dict[ERC20, WeiBalance]:
        tokens, balances, lastChangedBlock = self.vault.get_pool_tokens(self.id, block=block)
        return {ERC20(token): WeiBalance(balance, token, block=block) for token, balance in zip(tokens, balances)}

    @log(logger)
    def weights(self, block: Optional[Block] = None) -> List[int]:
        try:
            return self.contract.getNormalizedWeights(block_identifier = block)
        except (AttributeError,ValueError):
            return [1 for _ in self.tokens(block=block).keys()]


@log(logger)
@lru_cache(maxsize=None)
def _is_standard_pool(pool: EthAddress) -> bool:
    '''
    Returns `False` if `build_name(pool) in ['ConvergentCurvePool','MetaStablePool']`, else `True`
    '''
    
    # With `return_None_on_failure=True`, if `build_name(pool)` fails,
    # we can't know for sure that its a standard pool, but... it probably is.
    return build_name(pool, return_None_on_failure=True) not in ['ConvergentCurvePool','MetaStablePool']


class BalancerV2(metaclass=Singleton):
    def __init__(self) -> None:
        self.vaults = [BalancerV2Vault(vault) for vault in BALANCER_V2_VAULTS]
    
    def __str__(self) -> str:
        return "BalancerV2()"

    @log(logger)
    def is_pool(self, token_address: AnyAddressType) -> bool:
        methods = ['getPoolId()(bytes32)','getPausedState()((bool,uint,uint))','getSwapFeePercentage()(uint)']
        return has_methods(token_address, methods)
    
    @log(logger)
    def get_pool_price(self, pool_address: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
        return BalancerV2Pool(pool_address).get_pool_price(block=block)

    @log(logger)
    def get_token_price(self, token_address: Address, block: Optional[Block] = None) -> UsdPrice:
        deepest_pool = self.deepest_pool_for(token_address, block=block)
        if deepest_pool is None: return
        return deepest_pool.get_token_price(token_address, block)
    
    @log(logger)
    def deepest_pool_for(self, token_address: Address, block: Optional[Block] = None) -> Optional[BalancerV2Pool]:
        deepest_pools = {vault.address: vault.deepest_pool_for(token_address, block=block) for vault in self.vaults}
        deepest_pools = {vault: deepest_pool for vault,deepest_pool in deepest_pools.items() if deepest_pool is not None}
        deepest_pool_balance = max(pool_balance for pool_address, pool_balance in deepest_pools.values())
        for pool_address, pool_balance in deepest_pools.values():
            if pool_balance == deepest_pool_balance and pool_address:
                return BalancerV2Pool(pool_address)

balancer = BalancerV2()
