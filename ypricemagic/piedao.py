from ypricemagic.utils.utils import Contract_with_erc20_fallback
from brownie import Contract
from . import magic
from .utils.utils import get_decimals_with_override
import logging

# NOTE: If this module is not working with you, try to reinitialize your contract with 
# Contract.from_abi(). Get the proper abi from etherscan. For some reason, Contract()
# hasn't been pulling it correctly for me but this fix works. 

def is_pie(address):
    pool = Contract(address)
    required = {"getCap", "getPublicSwapSetter", "getTokenBinder"}
    return set(pool.__dict__) & required == required

def value(token, block, balance):
    logging.debug(f'token: {token}')
    if token == '0xf037f37f58110933834CA64545E4ffD169736561': # wrapped ATRI
        newtoken = '0xdacD69347dE42baBfAEcD09dC88958378780FB62' # ATRI
        return balance / 10 ** get_decimals_with_override(token) * magic.get_price(newtoken, block=block)
    return balance / 10 ** get_decimals_with_override(token) * magic.get_price(token, block=block)

def get_price(token, block=None):
    token = Contract(token)
    ten_tokens = 10 ** (token.decimals() + 1)
    balances = token.calcTokensForAmount(ten_tokens, block_identifier = block)
    logging.debug(f"pie balances: {balances}")
    total = sum(
        value(token, block, balance)
        for token, balance in zip(balances[0], balances[1])
    )
    return total/10

PPROXYPAUSABLE = [{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"stateMutability":"payable","type":"fallback"},{"inputs":[{"internalType":"address","name":"_value","type":"address"}],"name":"addressToBytes32","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"bytes32","name":"_value","type":"bytes32"}],"name":"bytes32ToAddress","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"bytes32","name":"_value","type":"bytes32"}],"name":"bytes32ToString","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"pure","type":"function"},{"inputs":[],"name":"getImplementation","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getPaused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getPauzer","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getProxyOwner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"_key","type":"bytes32"}],"name":"readAddress","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"_key","type":"bytes32"}],"name":"readBool","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"_key","type":"bytes32"}],"name":"readString","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renouncePauzer","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_newImplementation","type":"address"}],"name":"setImplementation","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bool","name":"_value","type":"bool"}],"name":"setPaused","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_newPauzer","type":"address"}],"name":"setPauzer","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_newOwner","type":"address"}],"name":"setProxyOwner","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"_key","type":"bytes32"}],"name":"storageRead","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"_value","type":"string"}],"name":"stringToBytes32","outputs":[{"internalType":"bytes32","name":"result","type":"bytes32"}],"stateMutability":"pure","type":"function"}]