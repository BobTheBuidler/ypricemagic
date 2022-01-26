import logging
from functools import lru_cache

from brownie import web3
from multicall import Call, Multicall
from y.contracts import Contract, has_methods
from y.decorators import log
from y.exceptions import ContractNotVerified
from ypricemagic.utils.multicall import fetch_multicall
from ypricemagic.utils.raw_calls import _decimals

logger = logging.getLogger(__name__)

# NOTE: Yearn and Yearn-like

@log(logger)
@lru_cache(maxsize=None)
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
        except ContractNotVerified: pass

    logger.debug(f'`is_yearn_vault({token})` returns `{result}`')
    return result


@log(logger)
def get_price(token, block=None):
    # v1 vaults use getPricePerFullShare scaled to 18 decimals
    # v2 vaults use pricePerShare scaled to underlying token decimals
    # yearnish clones use all sorts of other things, we gotchu covered

    share_price_methods = ['pricePerShare()(uint)','getPricePerShare()(uint)','getPricePerFullShare()(uint)','getSharesToUnderlying()(uint)','exchangeRate()(uint)']
    calls = [Call(token, [method], [[method, None]]) for method in share_price_methods]
    results = [result for result in Multicall(calls, _w3=web3, block_id=block, require_success=False)().values() if result is not None]
    assert len(results) in [1,0], 'Something is going wrong in yearn vault calculations. Must debug'
    if len(results) == 1: share_price = results[0]

    underlying_methods = ['token()(address)','underlying()(address)','native()(address)','want()(address)']
    calls = [Call(token, [method], [[method, None]]) for method in underlying_methods]
    results = [result for result in Multicall(calls, _w3=web3, block_id=block, require_success=False)().values() if result is not None]
    assert len(results) in [1,0], 'Something is going wrong in yearn vault calculations. Must debug'
    if len(results) == 1: underlying = results[0]

    decimals = _decimals(token)

    # saving for later
    '''
    vault = Contract(token)
    if hasattr(vault, 'pricePerShare'):
        share_price, underlying, decimals = fetch_multicall(
            [vault, 'pricePerShare'],
            [vault, 'token'],
            [vault, 'decimals'],
            block=block
        )
    elif hasattr(vault, 'getPricePerFullShare') and hasattr(vault, 'token'):
        share_price, underlying = fetch_multicall(
            [vault, 'getPricePerFullShare'],
            [vault, 'token'],
            block=block
        )
        decimals = 18
    elif hasattr(vault, 'getPricePerFullShare') and hasattr(vault, 'underlying'):
        share_price, underlying, decimals = fetch_multicall(
            [vault, 'getPricePerFullShare'],
            [vault, 'underlying'],
            [vault, 'decimals'],
            block=block
        )
    elif hasattr(vault, 'getPricePerFullShare') and hasattr(vault, 'native'):
        share_price, underlying, decimals = fetch_multicall(
            [vault, 'getPricePerFullShare'],
            [vault, 'native'],
            [vault, 'decimals'],
            block=block
        )
    elif hasattr(vault, 'getPricePerFullShare') and hasattr(vault, 'want'):
        share_price, underlying, decimals = fetch_multicall(
            [vault, 'getPricePerFullShare'],
            [vault, 'want'],
            [vault, 'decimals'],
            block=block
        )
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
    elif hasattr(vault, 'getPricePerShare'):
        share_price, underlying, decimals = fetch_multicall(
            [vault, 'getPricePerShare'],
            [vault, 'token'],
            [vault, 'decimals'],
            block=block
        )
    elif hasattr(vault,'exchangeRate'):
        share_price, underlying, decimals = fetch_multicall(
            [vault,'exchangeRate'],
            [vault,'underlying'],
            [vault,'decimals'],
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
    ''' might need this later for goofy L1s w/o multicall2        
    else:
        if hasattr(vault, 'pricePerShare'):
            share_price = vault.pricePerShare(block_identifier = block)
            underlying = vault.token(block_identifier = block)
            decimals = vault.decimals(block_identifier = block)
        elif hasattr(vault, 'getPricePerFullShare') and hasattr(vault, 'token'):
            share_price = vault.getPricePerFullShare(block_identifier = block)
            underlying = vault.token(block_identifier = block)
            decimals = 18
        elif hasattr(vault, 'getPricePerFullShare') and hasattr(vault, 'underlying'):
            share_price = vault.getPricePerFullShare(block_identifier = block)
            underlying = vault.underlying(block_identifier = block)
            decimals = vault.decimals(block_identifier = block)
        elif hasattr(vault, 'getPricePerFullShare') and hasattr(vault, 'want'):
            share_price = vault.getPricePerFullShare(block_identifier = block)
            underlying = vault.want(block_identifier = block)
            decimals = vault.decimals(block_identifier = block)
        elif hasattr(vault, 'getPricePerFullShare') and hasattr(vault, 'native'):
            share_price = vault.getPricePerFullShare(block_identifier=block)
            underlying = vault.native(block_identifier=block)
            decimals = vault.decimals(block_identifier=block)
        elif hasattr(vault, 'getPricePerShare'):
            share_price = vault.getPricePerShare(block_identifier = block)
            underlying = vault.token(block_identifier = block)
            decimals = vault.decimals(block_identifier = block)
            '''

    #try:
    price = [share_price / 10 ** decimals, underlying]
    #except TypeError: # when getPricePerShare() reverts due to divide by zero
    #    price = [1, underlying]
    #except UnboundLocalError: # not supported
    #    price = None
    
    if price: logger.debug("yearn -> %s", price)
    return price
