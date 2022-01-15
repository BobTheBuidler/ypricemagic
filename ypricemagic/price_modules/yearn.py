import logging

from joblib import logger
from y.contracts import Contract
from ypricemagic.utils.multicall import fetch_multicall

logger = logging.getLogger(__name__)

# NOTE: Yearn and Yearn-like

def is_yearn_vault(token):
    vault = Contract(token)
    # Yearn-like contracts can use these formats
    return any([
        hasattr(vault, 'pricePerShare'),
        hasattr(vault, 'getPricePerFullShare'),
        hasattr(vault, 'getPricePerShare'),
        hasattr(vault, 'exchangeRate') and hasattr(vault,'underlying'),
        hasattr(vault, 'getSharesToUnderlying')
        ])


def get_price(token, block=None):
    # v1 vaults use getPricePerFullShare scaled to 18 decimals
    # v2 vaults use pricePerShare scaled to underlying token decimals
    # yearnish clones use all sorts of other things, we gotchu covered
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

    try:
        price = [share_price / 10 ** decimals, underlying]
    except TypeError: # when getPricePerShare() reverts due to divide by zero
        price = [1, underlying]
    
    if price: logger.debug("yearn -> %s", price)
    return price
