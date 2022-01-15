import logging

from y.contracts import Contract
from ypricemagic.classes import ERC20
from ypricemagic.utils.events import decode_logs, get_logs_asap
from ypricemagic.utils.multicall import fetch_multicall

logger = logging.getLogger(__name__)


class BalancerV2Vault:
    def __init__(self, vault_address) -> None:
        self.address = vault_address
        self.contract = Contract(self.address)
    
    def get_pool_tokens(self, pool_id: int, block=None):
        a = self.contract.getPoolTokens(pool_id, block_identifier = block)
        logger.debug(a)
        return a

    def list_pools(self, block=None):
        topics = ['0x3c13bc30b8e878c53fd2a36b679409c073afd75950be43d8858768e956fbc20e']
        events = decode_logs(get_logs_asap(self.address, topics, to_block=block))
        return {event['poolId'].hex():event['poolAddress'] for event in events}

    def deepest_pool_for(self, token_address, block=None):
        pools = self.list_pools(block=block)
        pools_info = fetch_multicall(*[[self.contract,'getPoolTokens',poolId] for poolId in pools.keys()], block=block)
        deepest_pool = {'pool': None, 'balance': 0}
        for pool, info in zip(pools.values(),pools_info):
            if str(info) == "((), (), 0)": continue
            ct_tokens = len(info[0])
            pool_balances = {info[0][i]: info[1][i] for i in range(ct_tokens)}
            for token, balance in pool_balances.items():
                try:
                    if (
                        token == token_address and balance > deepest_pool['balance']
                        and ERC20(pool).build_name not in ['ConvergentCurvePool','MetaStablePool']
                        ):
                        deepest_pool = {'pool': pool, 'balance': balance}
                except ValueError as e:
                    if 'source code not verified' in str(e): pass
                    else: raise
        return deepest_pool['pool'], deepest_pool['balance']

    
        
