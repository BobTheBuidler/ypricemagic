from typing import Type
from brownie import Contract
from .utils.multicall2 import fetch_multicall


def is_yearn_vault(token):
    vault = Contract(token)
    return hasattr(vault, 'pricePerShare') or hasattr(vault, 'getPricePerFullShare')\
        or hasattr(vault, 'getPricePerShare') # Yearn-like contracts can use this format


def get_price(token, block=None):
    # v1 vaults use getPricePerFullShare scaled to 18 decimals
    # v2 vaults use pricePerShare scaled to underlying token decimals
    vault = Contract(token)
    if hasattr(vault, 'pricePerShare'):
        share_price, underlying, decimals = fetch_multicall(
            [vault, 'pricePerShare'],
            [vault, 'token'],
            [vault, 'decimals'],
            block=block
        )
    if hasattr(vault, 'getPricePerFullShare'):
        share_price, underlying = fetch_multicall(
            [vault, 'getPricePerFullShare'],
            [vault, 'token'],
            block=block
        )
        decimals = 18
    if hasattr(vault, 'getPricePerShare'):
        share_price, underlying, decimals = fetch_multicall(
            [vault, 'getPricePerShare'],
            [vault, 'token'],
            [vault, 'decimals'],
            block=block
        )

    try:
        return [share_price / 10 ** decimals, underlying]
    except TypeError: # when getPricePerShare() reverts due to divide by zero
        return [0, underlying]
