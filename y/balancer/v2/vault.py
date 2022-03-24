import logging
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

from brownie.convert.datatypes import EthAddress
from hexbytes import HexBytes
from y.classes.common import ContractBase
from y.contracts import build_name
from y.decorators import log
from y.typing import Block
from y.utils.events import decode_logs, get_logs_asap
from y.utils.multicall import fetch_multicall

logger = logging.getLogger(__name__)


class BalancerV2Vault(ContractBase):
    def __init__(self, address: str, *args: Any, **kwargs: Any) -> None:
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
    def deepest_pool_for(self, token_address: EthAddress, block: Optional[Block] = None) -> Tuple[Optional[EthAddress],int]:
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


@log(logger)
@lru_cache(maxsize=None)
def _is_standard_pool(pool: EthAddress) -> bool:
    '''
    Returns `False` if `build_name(pool) in ['ConvergentCurvePool','MetaStablePool']`, else `True`
    '''
    
    # With `return_None_on_failure=True`, if `build_name(pool)` fails,
    # we can't know for sure that its a standard pool, but... it probably is.
    return build_name(pool, return_None_on_failure=True) not in ['ConvergentCurvePool','MetaStablePool']
