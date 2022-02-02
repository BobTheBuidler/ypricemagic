import logging
from functools import cached_property, lru_cache

from y.classes.common import ERC20, WeiBalance
from y.contracts import Contract, has_methods, probe
from y.decorators import log
from y.exceptions import ContractNotVerified, MessedUpBrownieContract, CantFetchParam
from y.utils.cache import memory

logger = logging.getLogger(__name__)

# NOTE: Yearn and Yearn-inspired

@log(logger)
def get_price(token: str, block=None):
    return YearnInspiredVault(token).price(block=block)


@log(logger)
@memory.cache()
def is_yearn_vault(token):
    logger.debug(f'Checking `is_yearn_vault({token})')
    # Yearn-like contracts can use these formats
    result = any([
        has_methods(token, ['pricePerShare()(uint)','getPricePerShare()(uint)','getPricePerFullShare()(uint)','getSharesToUnderlying()(uint)'], any),
        has_methods(token, ['exchangeRate()(uint)','underlying()(address)']),
    ])

    # pricePerShare can revert if totalSupply == 0, which would cause `has_methods` to return `False`,
    # but it might still be a vault. This section will correct `result` for problematic vaults.
    if result is False:
        try: 
            contract = Contract(token)
            result = any([
                hasattr(contract,'pricePerShare'),
                hasattr(contract,'getPricePerShare'),
                hasattr(contract,'getPricePerFullShare'),
                hasattr(contract,'getSharesToUnderlying'),
            ])
        except (ContractNotVerified, MessedUpBrownieContract): pass

    logger.debug(f'`is_yearn_vault({token})` returns `{result}`')
    return result


class YearnInspiredVault(ERC20):
    # v1 vaults use getPricePerFullShare scaled to 18 decimals
    # v2 vaults use pricePerShare scaled to underlying token decimals
    # yearnish clones use all sorts of other things, we gotchu covered
    def __init__(self, address: str, *args, **kwargs):
        super().__init__(address, *args, **kwargs)
    
    def __repr__(self) -> str:
        if self.symbol:
            return f"<YearnInspiredVault {self.symbol} '{self.address}'>"
    
    @cached_property
    @log(logger)
    def underlying(self) -> ERC20:
        methods = ['token()(address)','underlying()(address)','native()(address)','want()(address)','wmatic()(address)','wbnb()(address)','based()(address)']
        underlying = probe(self.address, methods)
        if underlying: return ERC20(underlying)
        else: raise CantFetchParam(f'underlying for {self.__repr__()}')

    @log(logger)
    @lru_cache
    def share_price(self, block: int = None) -> WeiBalance:
        methods = ['pricePerShare()(uint)','getPricePerShare()(uint)','getPricePerFullShare()(uint)','getSharesToUnderlying()(uint)','exchangeRate()(uint)']
        share_price = probe(self.address, methods, block=block)
        if share_price: return WeiBalance(share_price, self.underlying, block=block)
        else: raise CantFetchParam(f'share_price for {self.__repr__()}')
    
    @log(logger)
    @lru_cache
    def price(self, block: int = None) -> float:
        return self.share_price(block=block).readable * self.underlying.price(block=block)

    # saving for later
    '''
    elif hasattr(vault, 'getPricePerFullShare') and hasattr(vault, 'token'):
        share_price, underlying = fetch_multicall(
            [vault, 'getPricePerFullShare'],
            [vault, 'token'],
            block=block
        )
        decimals = 18
        
    elif vault.__dict__['_build']['contractName'] == 'BeefyVaultV6Matic':
        share_price, underlying, decimals = fetch_multicall(
            [vault, 'getPricePerFullShare'],
            [vault, 'wmatic'],
            [vault, 'decimals'],
            block=block
        )
    elif vault.__dict__['_build']['contractName'] == 'BeefyVenusVaultBNB':
        share_price, underlying, decimals = fetch_multicall(
            [vault, 'getPricePerFullShare'],
            [vault, 'wbnb'],
            [vault, 'decimals'],
            block=block
        )
        
    elif hasattr(vault,'getSharesToUnderlying'):
        underlying, decimals = fetch_multicall(
            [vault,'token'],
            [vault,'decimals'],
            block=block
        )
        share_price = vault.getSharesToUnderlying(10 ** decimals,block_identifier=block)
    '''
