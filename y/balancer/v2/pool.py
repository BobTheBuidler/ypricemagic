
import logging
from functools import cached_property
from typing import Dict, List, Optional

from brownie import web3
from multicall import Call
from y.balancer.v2.vault import BalancerV2Vault
from y.classes.common import ERC20, WeiBalance
from y.constants import STABLECOINS, WRAPPED_GAS_COIN
from y.datatypes import UsdPrice, UsdValue
from y.decorators import log
from y.typing import Block
from y.utils.raw_calls import raw_call

logger = logging.getLogger(__name__)

class PoolId(int):
    def __init__(self, v) -> None:
        super().__init__()

class BalancerV2Pool(ERC20):
    def __init__(self, pool_address) -> None:
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
    def get_token_price(self, token_address: str, block: Optional[Block] = None) -> Optional[UsdPrice]:
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
