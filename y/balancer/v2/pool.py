
import logging
from functools import cached_property
from typing import Dict, List

from brownie import web3
from multicall import Call
from y.balancer.v2.vault import BalancerV2Vault
from y.classes.common import ERC20
from y.constants import STABLECOINS, WRAPPED_GAS_COIN, usdc
from y.decorators import log
from y.prices import magic
from y.utils.multicall import multicall_decimals
from y.utils.raw_calls import _decimals, raw_call

logger = logging.getLogger(__name__)

class BalancerV2Pool(ERC20):
    def __init__(self, pool_address) -> None:
        super().__init__(pool_address)

    @cached_property
    @log(logger)
    def id(self):
        return Call(self.address, ['getPoolId()(bytes32)'], [['id',None]], _w3=web3)()['id']
    
    @cached_property
    @log(logger)
    def vault(self):
        vault = raw_call(self.address,'getVault()',output='address')
        return BalancerV2Vault(vault)

    @log(logger)
    def get_pool_price(self, block=None):
        return self.get_tvl(block=block) / self.total_supply_readable(block=block)

    @log(logger)
    def get_tvl(self, block=None):
        return sum(balance * token.price(block=block) for token, balance in self.get_balances(block=block).items())

    @log(logger)
    def get_balances(self, block=None):
        token_balances = self.tokens(block=block)
        decimals = multicall_decimals(token_balances.keys(), block)
        return {token: balance / 10 ** decimal for token, balance, decimal in zip(token_balances.keys(), token_balances.values(), decimals)}

    @log(logger)
    def get_token_price(self, token_address: str, block=None) -> float:
        token_balances = self.tokens(block=block)
        weights = self.weights(block=block)
        pool_tokens = list(zip(token_balances.keys(),token_balances.values(), weights))
        wethBal, usdcBal, pairedTokenBal = None, None, None
        for pool_token, balance, weight in pool_tokens:
            if pool_token in STABLECOINS:
                usdcBal, usdcWeight = balance, weight
            if pool_token == WRAPPED_GAS_COIN:
                wethBal, wethWeight = balance, weight
            if pool_token == token_address:
                tokenBal, tokenWeight = balance, weight
            if len(pool_tokens) == 2 and pool_token != token_address:
                pairedTokenBal, pairedTokenWeight, pairedToken = balance, weight, pool_token

        tokenPrice = None
        if usdcBal:
            usdcValueUSD = (usdcBal / 10 ** 6) * magic.get_price(usdc, block)
            tokenValueUSD = usdcValueUSD / usdcWeight * tokenWeight
            tokenPrice = tokenValueUSD / (tokenBal / 10 ** _decimals(token_address,block))
        elif wethBal:
            wethValueUSD = (wethBal / 10 ** 18) * magic.get_price(WRAPPED_GAS_COIN, block)
            tokenValueUSD = wethValueUSD / wethWeight * tokenWeight
            tokenPrice = tokenValueUSD / (tokenBal / 10 ** _decimals(token_address,block))
        elif pairedTokenBal:
            pairedTokenValueUSD = (pairedTokenBal / 10 ** _decimals(pairedToken,block)) * magic.get_price(pairedToken, block)
            tokenValueUSD = pairedTokenValueUSD / pairedTokenWeight * tokenWeight
            tokenPrice = tokenValueUSD / (tokenBal / 10 ** _decimals(token_address,block))
        return tokenPrice
    
    @log(logger)
    def tokens(self, block=None) -> Dict[ERC20, float]:
        tokens, balances, lastChangedBlock = self.vault.get_pool_tokens(self.id, block=block)
        return {token: balance for token, balance in zip(tokens, balances)}        

    @log(logger)
    def weights(self, block=None) -> List[int]:
        try:
            return self.contract.getNormalizedWeights(block_identifier = block)
        except (AttributeError,ValueError):
            return [1 for _ in self.tokens(block=block).keys()]
