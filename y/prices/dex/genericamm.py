import asyncio
from typing import Optional, Tuple

import a_sync
from brownie.exceptions import ContractNotFound

from y import ENVIRONMENT_VARIABLES as ENVS
from y import Contract
from y.classes.common import ERC20, WeiBalance
from y.datatypes import AnyAddressType, Block, UsdPrice, UsdValue
from y.decorators import stuck_coro_debugger
from y.exceptions import ContractNotVerified, MessedUpBrownieContract
from y.utils import gather_methods, hasall
from y.utils.cache import memory

_CHECK_METHODS = 'getReserves','token0','token1'
_TOKEN_METHODS = 'token0()(address)', 'token1()(address)'

@memory.cache()
def is_generic_amm(lp_token_address: AnyAddressType) -> bool:
    try:
        return hasall(Contract(lp_token_address), _CHECK_METHODS)
    except (ContractNotFound, ContractNotVerified):
        return False
    except MessedUpBrownieContract:
        # probably false, can get more specific when there's a need.
        return False
        
class GenericAmm(a_sync.ASyncGenericBase):
    def __init__(self, asynchronous: bool = False) -> None:
        self.asynchronous = asynchronous

    def __contains__(self, lp_token_address: AnyAddressType) -> bool:
        return is_generic_amm(lp_token_address)
    
    @stuck_coro_debugger
    async def get_price(self, lp_token_address: AnyAddressType, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> UsdPrice:
        tvl, total_supply = await asyncio.gather(
            self.get_tvl(lp_token_address, block=block, skip_cache=skip_cache, sync=False),
            ERC20(lp_token_address, asynchronous=True).total_supply_readable(block=block),
        )
        if total_supply is None:
            return None
        elif total_supply == 0:
            return 0
        return UsdPrice(tvl / total_supply)
    
    @stuck_coro_debugger
    @a_sync.a_sync(cache_type='memory')
    async def get_tokens(self, lp_token_address: AnyAddressType) -> Tuple[ERC20,ERC20]:
        tokens = await gather_methods(lp_token_address, _TOKEN_METHODS)
        return tuple(ERC20(token, asynchronous=self.asynchronous) for token in tokens)
    
    @stuck_coro_debugger
    async def get_tvl(self, lp_token_address: AnyAddressType, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> UsdValue:
        lp_token_contract = await Contract.coroutine(lp_token_address)
        tokens = await self.get_tokens(lp_token_address, sync=False)
        reserves = await lp_token_contract.getReserves.coroutine(block_identifier=block)
        reserves = [WeiBalance(reserve, token, block=block, skip_cache=skip_cache) for token, reserve in zip(tokens,reserves)]
        return UsdValue(sum(await asyncio.gather(*[reserve.__value_usd__(sync=False) for reserve in reserves])))


generic_amm = GenericAmm(asynchronous=True)
