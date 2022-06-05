from functools import lru_cache
from typing import Optional, Tuple

from async_lru import alru_cache
from brownie.exceptions import ContractNotFound
from multicall import Call
from multicall.utils import await_awaitable, gather
from y import Contract
from y.classes.common import ERC20, WeiBalance
from y.datatypes import AnyAddressType, Block, UsdPrice, UsdValue
from y.exceptions import ContractNotVerified, MessedUpBrownieContract
from y.utils.cache import memory


@memory.cache()
def is_generic_amm(lp_token_address: AnyAddressType) -> bool:
    try:
        token_contract = Contract(lp_token_address)
        return all(hasattr(token_contract, attr) for attr in ['getReserves','token0','token1'])
    except (ContractNotFound, ContractNotVerified):
        return False
    except MessedUpBrownieContract:
        # probably false, can get more specific when there's a need.
        return False
        
class GenericAmm:
    def __contains__(self, lp_token_address: AnyAddressType) -> bool:
        return is_generic_amm(lp_token_address)
    
    def get_price(self, lp_token_address: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
        return await_awaitable(self.get_price_async(lp_token_address, block=block))
    
    async def get_price_async(self, lp_token_address: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
        tvl, total_supply = await gather([
            self.get_tvl_async(lp_token_address, block=block),
            ERC20(lp_token_address).total_supply_readable_async(block=block),
        ])
        if total_supply is None:
            return None
        elif total_supply == 0:
            return 0
        return UsdPrice(tvl / total_supply)

    @lru_cache(maxsize=None)
    def get_tokens(self, lp_token_address: AnyAddressType) -> Tuple[ERC20,ERC20]:
        return await_awaitable(self.get_tokens_async(lp_token_address))
    
    @alru_cache(maxsize=None)
    async def get_tokens_async(self, lp_token_address: AnyAddressType) -> Tuple[ERC20,ERC20]:
        tokens = await gather([
            Call(lp_token_address, ['token0()(address)']).coroutine(),
            Call(lp_token_address, ['token1()(address)']).coroutine(),
        ])
        return ERC20(tokens[0]), ERC20(tokens[1])
    
    def get_tvl(self, lp_token_address: AnyAddressType, block: Optional[Block] = None) -> UsdValue:
        return await_awaitable(self.get_tvl_async(lp_token_address, block=block))
    
    async def get_tvl_async(self, lp_token_address: AnyAddressType, block: Optional[Block] = None) -> UsdValue:
        lp_token_contract = Contract(lp_token_address)
        tokens = await self.get_tokens_async(lp_token_address)
        reserves = await lp_token_contract.getReserves.coroutine(block_identifier=block)
        reserves = [WeiBalance(reserve,token,block) for token, reserve in zip(tokens,reserves)]
        return UsdValue(sum(await gather([reserve.value_usd_async for reserve in reserves])))


generic_amm = GenericAmm()
