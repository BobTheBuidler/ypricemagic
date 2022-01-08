from brownie import Contract
from interfaces.ERC20 import ERC20ABI


def Contract_with_erc20_fallback(address):
    try:
        contract = Contract(address)
    except (AttributeError, ValueError, IndexError):
        contract = Contract_erc20(address)
    return contract

def Contract_erc20(address):
    return Contract.from_abi('ERC20',address,ERC20ABI)
