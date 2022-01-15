
from joblib import Parallel, delayed
from y.constants import usdc, weth
from ypricemagic import magic
from ypricemagic.classes import ERC20
from ypricemagic.price_modules.balancer.v2.vault import BalancerV2Vault
from ypricemagic.utils.multicall import fetch_multicall, multicall_decimals
from ypricemagic.utils.raw_calls import _decimals


class BalancerV2Pool(ERC20):
    def __init__(self, pool_address) -> None:
        super().__init__(pool_address)
        self.id, vault = fetch_multicall([self.contract, 'getPoolId'],[self.contract,'getVault'])
        self.vault = BalancerV2Vault(vault)

    def is_pool(self):
        required = {'getPoolId','getPausedState','getSwapFeePercentage'}
        return set(self.contract.__dict__) & required == required

    def get_pool_price(self, block=None):
        return self.get_tvl(block=block) / self.total_supply(block=block)

    def get_tvl(self, block=None):
        balances = self.get_balances(block=block)
        prices = Parallel(4,'threading')(delayed(magic.get_price)(token, block) for token in balances.keys())
        return sum(balance * price for balance, price in zip(balances.values(), prices))

    def get_balances(self, block=None):
        token_balances = self.tokens(block=block)
        decimals = multicall_decimals(token_balances.keys(), block)
        return {token: balance / 10 ** decimal for token, balance, decimal in zip(token_balances.keys(), token_balances.values(), decimals)}

    def get_token_price(self, token_address, block=None):
        token_balances = self.tokens(block=block)
        weights = self.weights(block=block)
        pool_tokens = list(zip(token_balances.keys(),token_balances.values(), weights))
        wethBal, usdcBal, pairedTokenBal = None, None, None
        for pool_token, balance, weight in pool_tokens:
            if pool_token == usdc:
                usdcBal, usdcWeight = balance, weight
            if pool_token == weth:
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
            wethValueUSD = (wethBal / 10 ** 18) * magic.get_price(weth, block)
            tokenValueUSD = wethValueUSD / wethWeight * tokenWeight
            tokenPrice = tokenValueUSD / (tokenBal / 10 ** _decimals(token_address,block))
        elif pairedTokenBal:
            pairedTokenValueUSD = (pairedTokenBal / 10 ** _decimals(pairedToken,block)) * magic.get_price(pairedToken, block)
            tokenValueUSD = pairedTokenValueUSD / pairedTokenWeight * tokenWeight
            tokenPrice = tokenValueUSD / (tokenBal / 10 ** _decimals(token_address,block))
        return tokenPrice
    
    def tokens(self, block=None):
        tokens, balances, lastChangedBlock = self.vault.get_pool_tokens(self.id, block=block)
        return {token: balance for token, balance in zip(tokens, balances)}        

    def weights(self, block=None):
        try:
            return self.contract.getNormalizedWeights(block_identifier = block)
        except (AttributeError,ValueError):
            return [1 for _ in self.tokens(block=block).keys()]
