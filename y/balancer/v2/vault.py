import logging
from functools import lru_cache

from y.classes.common import ContractBase
from y.contracts import build_name
from y.decorators import log
from y.utils.events import decode_logs, get_logs_asap
from y.utils.multicall import fetch_multicall

logger = logging.getLogger(__name__)


class BalancerV2Vault(ContractBase):
    def __init__(self, address: str, *args, **kwargs):
        super().__init__(address, *args, **kwargs)
        if not self._is_cached:
            # we need the contract cached so we can decode logs correctly
            self.contract
    
    @log(logger)
    def get_pool_tokens(self, pool_id: int, block=None):
        return self.contract.getPoolTokens(pool_id, block_identifier = block)

    @log(logger)
    @lru_cache
    def list_pools(self, block=None):
        topics = ['0x3c13bc30b8e878c53fd2a36b679409c073afd75950be43d8858768e956fbc20e']
        events = decode_logs(get_logs_asap(self.address, topics, to_block=block))
        return {event['poolId'].hex():event['poolAddress'] for event in events}

    @log(logger)
    def deepest_pool_for(self, token_address, block=None):
        pools = self.list_pools(block=block)
        poolids = [poolid for poolid, pool in pools.items() if _is_standard_pool(pool)]
        pools_info = fetch_multicall(*[[self.contract,'getPoolTokens',poolId] for poolId in poolids], block=block)
        deepest_pool = {'pool': None, 'balance': 0}
        pools_info = {pool: info for pool, info in zip(pools.values(), pools_info) if str(info) != "((), (), 0)"}
        for pool, info in zip(pools.values(),pools_info):
            ct_tokens = len(info[0])
            pool_balances = {info[0][i]: info[1][i] for i in range(ct_tokens)}
            pool_balance = [balance for token, balance in pool_balances.items() if token == token_address]
            if len(pool_balance) == 0: continue
            
            assert len(pool_balance) == 1
            pool_balance = pool_balance[0]

            if pool_balance > deepest_pool['balance']:
                deepest_pool = {'pool': pool, 'balance': pool_balance}

        return deepest_pool['pool'], deepest_pool['balance']


@log(logger) 
def _is_standard_pool(pool: str):
    '''
    Returns `False` if `build_name(pool) in ['ConvergentCurvePool','MetaStablePool']`, else `True`
    '''
    
    # With `return_None_on_failure=True`, if `build_name(pool)` fails,
    # we can't know for sure that its a standard pool, but... it probably is.
    return build_name(pool, return_None_on_failure=True) not in ['ConvergentCurvePool','MetaStablePool']
