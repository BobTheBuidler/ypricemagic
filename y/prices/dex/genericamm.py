from functools import lru_cache
from typing import Optional, Tuple

from brownie.convert.datatypes import EthAddress
from brownie.exceptions import ContractNotFound
from y import Contract
from y.classes.common import ERC20, WeiBalance
from y.datatypes import UsdPrice, UsdValue
from y.exceptions import ContractNotVerified, MessedUpBrownieContract
from y.typing import AnyAddressType, Block
from y.utils.cache import memory
from y.utils.multicall import fetch_multicall


@memory.cache()
def is_generic_amm(lp_token_address: AnyAddressType) -> bool:
    try:
        token_contract = Contract(lp_token_address)
        return all(hasattr(token_contract, attr) for attr in ['getReserves','token0','token1'])
    except (ContractNotFound, ContractNotVerified):
        return False
    except MessedUpBrownieContract:
        # probably false
        return False
        
class GenericAmm:
    def __contains__(self, lp_token_address: AnyAddressType) -> bool:
        return is_generic_amm(lp_token_address)
    
    def get_price(self, lp_token_address: AnyAddressType, block: Optional[Block] = None) -> UsdPrice:
        lp_token_contract = Contract(lp_token_address)
        total_supply, decimals = fetch_multicall(*[[lp_token_contract, attr] for attr in ['totalSupply','decimals']], block=block)
        total_supply_readable = total_supply / 10 ** decimals
        return UsdPrice(self.get_tvl(lp_token_address, block) / total_supply_readable)

    @lru_cache(maxsize=None)
    def get_tokens(self, lp_token_address: AnyAddressType) -> Tuple[ERC20,ERC20]:
        lp_token_contract = Contract(lp_token_address)
        tokens = fetch_multicall(*[[lp_token_contract,attr] for attr in ['token0', 'token1']])
        return ERC20(tokens[0]), ERC20(tokens[1])
    
    def get_tvl(self, lp_token_address: AnyAddressType, block: Optional[Block] = None) -> UsdValue:
        lp_token_contract = Contract(lp_token_address)
        tokens = self.get_tokens(lp_token_address)
        reserves = lp_token_contract.getReserves(block_identifier=block)
        reserves = [WeiBalance(reserve,token,block) for token, reserve in zip(tokens,reserves)]
        return UsdValue(sum(reserve.value_usd() for reserve in reserves))


generic_amm = GenericAmm()
