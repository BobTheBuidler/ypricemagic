from brownie import chain
from y.constants import dai, usdc, wbtc, weth
from y.contracts import Contract
from y.networks import Network
from ypricemagic import magic
from ypricemagic.price_modules.balancer.v1.pool import BalancerV1Pool
from ypricemagic.utils.raw_calls import _decimals

EXCHANGE_PROXY = {
    Network.Mainnet: '0x3E66B66Fd1d0b02fDa6C811Da9E0547970DB2f21',
}.get(chain.id, None)


class BalancerV1:
    def __init__(self) -> None:
        self.exchange_proxy = Contract(EXCHANGE_PROXY) if EXCHANGE_PROXY else None
    
    def is_pool(self, token_address):
        return BalancerV1Pool(token_address).is_pool()
    
    def get_pool_price(self, token_address, block=None):
        pool = BalancerV1Pool(token_address)
        assert pool.is_pool()
        return pool.get_pool_price(block=block)


    def get_token_price(self, token_address, block=None):
        out, totalOutput = self.get_some_output(token_address, block=block)
        if out: return (totalOutput / 10 ** _decimals(out,block)) * magic.get_price(out, block)
        # Can we get an output if we try smaller size?
        scale = 0.5
        out, totalOutput = self.get_some_output(token_address, block=block, scale=scale) 
        if out: return (totalOutput / 10 ** _decimals(out,block)) * magic.get_price(out, block) / scale
        # How about now? 
        scale = 0.1
        out, totalOutput = self.get_some_output(token_address, block=block, scale=scale)
        if out: return (totalOutput / 10 ** _decimals(out,block)) * magic.get_price(out, block) / scale
        else: return

    def check_liquidity_against(self, token_in, token_out, scale=1, block=None):
        output = self.exchange_proxy.viewSplitExactIn(
            token_in, token_out, 10 ** _decimals(token_in) * scale, 32 # NOTE: 32 is max
            , block_identifier = block
        )['totalOutput']
        return token_out, output

    def get_some_output(self, token_in, scale=1, block=None):
        try:
            out, totalOutput = self.check_liquidity_against(token_in, weth, block=block)
        except ValueError:
            try:
                out, totalOutput = self.check_liquidity_against(token_in, dai, block=block)
            except ValueError:
                try:
                    out, totalOutput = self.check_liquidity_against(token_in, usdc, block=block)
                except ValueError:
                    try:
                        out, totalOutput = self.check_liquidity_against(token_in, wbtc, block=block)
                    except ValueError:
                        out = None
                        totalOutput = None
        return out, totalOutput
