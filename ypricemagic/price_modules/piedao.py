import logging
from functools import lru_cache

from brownie import web3
from multicall import Call
from y.contracts import has_method
from y.decorators import log
from y.erc20 import decimals, totalSupplyReadable
from ypricemagic import magic
from ypricemagic.utils.multicall import multicall_balanceOf
from ypricemagic.utils.raw_calls import _decimals, raw_call

logger = logging.getLogger(__name__)


@log(logger)
@lru_cache
def is_pie(address):
    logger.debug(f'Checking `is_pie({address})')
    result = has_method(address, "getTokenBinder()(address)")
    logger.debug(f'`is_pie({address}` returns `{result}`')
    return result

@log(logger)
def get_price(pie_address: str, block=None):
    logger.debug(f'fetching `piedao.get_price({pie_address}, {block})')
    price = tvl(pie_address, block) / totalSupplyReadable(pie_address, block)
    logger.debug(f'`piedao.get_price({pie_address}, {block})` returns `{price}`')
    return price

@log(logger)
def get_tokens(pie_address: str, block: int = None):
    logger.debug(f'fetching tokens for pie {pie_address} at block {block}')
    tokens = Call(pie_address, ['getTokens()(address[])'], returns=None, _w3=web3, block_id=block)()
    logger.debug(f'pie tokens at block {block}: {tokens}')
    return tokens

@log(logger)
def get_bpool(pie_address: str, block: int = None):
    logger.debug(f'fetching bpool for pie {pie_address} at block {block}')
    bpool = raw_call(pie_address, 'getBPool()', output='address', block=block)
    logger.debug(f'pie bpool at block {block}: {bpool}')
    return bpool

@log(logger)
def tvl(pie_address: str, block: int = None):
    tokens = get_tokens(pie_address, block)
    bpool = get_bpool(pie_address, block)
    token_balances = multicall_balanceOf(tokens, bpool, block=block)
    token_decimals = decimals(tokens, block)
    token_balances = [bal / 10 ** decimal for bal, decimal in zip(token_balances, token_decimals)]
    prices = magic.get_prices(tokens, block, silent=True, dop=1)
    return sum(bal * price for bal, price in zip(token_balances, prices))

# currently unused:
PPROXYPAUSABLE = [{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"stateMutability":"payable","type":"fallback"},{"inputs":[{"internalType":"address","name":"_value","type":"address"}],"name":"addressToBytes32","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"bytes32","name":"_value","type":"bytes32"}],"name":"bytes32ToAddress","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"bytes32","name":"_value","type":"bytes32"}],"name":"bytes32ToString","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"pure","type":"function"},{"inputs":[],"name":"getImplementation","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getPaused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getPauzer","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getProxyOwner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"_key","type":"bytes32"}],"name":"readAddress","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"_key","type":"bytes32"}],"name":"readBool","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"_key","type":"bytes32"}],"name":"readString","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renouncePauzer","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_newImplementation","type":"address"}],"name":"setImplementation","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bool","name":"_value","type":"bool"}],"name":"setPaused","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_newPauzer","type":"address"}],"name":"setPauzer","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_newOwner","type":"address"}],"name":"setProxyOwner","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"_key","type":"bytes32"}],"name":"storageRead","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"_value","type":"string"}],"name":"stringToBytes32","outputs":[{"internalType":"bytes32","name":"result","type":"bytes32"}],"stateMutability":"pure","type":"function"}]

@log(logger)
def _value(token, block, balance):
    logging.debug(f'token: {token}')
    if token == '0xf037f37f58110933834CA64545E4ffD169736561': # wrapped ATRI
        newtoken = '0xdacD69347dE42baBfAEcD09dC88958378780FB62' # ATRI
        return balance / 10 ** _decimals(token) * magic.get_price(newtoken, block=block)
    return balance / 10 ** _decimals(token) * magic.get_price(token, block=block)