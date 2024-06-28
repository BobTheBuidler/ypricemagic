import logging
from typing import TYPE_CHECKING, Optional

from brownie import Contract as BrownieContract
from brownie.exceptions import CompilerError
from web3.exceptions import ContractLogicError

from y.datatypes import AnyAddressType

if TYPE_CHECKING:
    from y.prices.dex.uniswap.v2 import UniswapV2Pool

logger = logging.getLogger(__name__)

# General

class yPriceMagicError(ValueError):
    def __init__(self, exc: Exception, address: str, block: Optional[int], symbol: str):
        from y import Network
        self.exception = exc
        detail = exc.__class__.__name__
        if not isinstance(self.exception, PriceError):
            detail += f'({exc})'
        super().__init__(f"{detail} while fetching {Network.printable()} {symbol} {address} at block {block}")

class PriceError(Exception):
    def __init__(self, logger: logging.Logger, symbol: str):
        super().__init__(f"No price found for {symbol} {logger.address} at block {logger.block}")

class UnsupportedNetwork(Exception):
    pass

class NonStandardERC20(Exception):
    pass

class CantFetchParam(Exception):
    pass

class NoBlockFound(Exception):
    pass

class TokenError(ValueError):
    """Raised when a token contract is not the correct contract type for the desired operation."""
    def __init__(self, token: AnyAddressType, desired_type: str):
        super().__init__(f"{token} is not a {desired_type}")

# Explorer Exceptions

class ExplorerError(Exception):  # don't want these caught by general exc clauses
    ...

class InvalidAPIKeyError(ExplorerError):
    _msg = "The block explorer for this network says your API key is invalid."
    def __init__(self, msg: str = ''):
        super().__init__(msg or self._msg)

# Contracts

class ContractNotVerified(ExplorerError):
    pass

class NoProxyImplementation(Exception):
    pass

class MessedUpBrownieContract(Exception):
    def __init__(self, address, *args: object) -> None:
        super().__init__(*args)
        # try to recache the contract
        try: BrownieContract.from_explorer(address)
        except CompilerError: pass # didn't work, oh well
        except Exception as e:
            if "invalid literal for int() with base 16: ''" in str(e): pass # didn't work, oh well
            elif "list index out of range" in str(e): pass # didn't work, oh well
            elif "pop from an empty deque" in str(e): pass # didn't work, oh well
            elif "'UsingForDirective' object has no attribute 'typeName'" in str(e): pass # didn't work, oh well
            elif contract_not_verified(e): pass # not verified, won't work
            else: raise


def contract_not_verified(e: Exception) -> bool:
    triggers = [
        'Contract source code not verified',
        'has not been verified',
    ]
    return any(trigger in str(e) for trigger in triggers)


# Pool detection

class NotAUniswapV2Pool(Exception):
    # NOTE: we use this exc to get the non-pool out of the pool singleton so it doesn't grow forever
    # TODO: Refactor this goofy thing out
    def __init__(self, non_pool: "UniswapV2Pool"):
        from y.prices.dex.uniswap.v2 import UniswapV2Pool
        UniswapV2Pool._ChecksumASyncSingletonMeta__instances[True].pop(non_pool.address, None)
        UniswapV2Pool._ChecksumASyncSingletonMeta__instances[False].pop(non_pool.address, None)
        super().__init__(non_pool.address)

class NotABalancerV2Pool(Exception):
    pass

# Uni

class CantFindSwapPath(Exception):
    pass

class TokenNotFound(ValueError):
    def __init__(self, token, container):
        super().__init__(f"{token} is not in {container}")

# Calls

class CalldataPreparationError(Exception):
    pass

class CallReverted(Exception):
    pass


def call_reverted(e: Exception) -> bool:
    if isinstance(e, ContractLogicError):
        return True
    triggers = [
        'execution reverted',
        'No data was returned - the call likely reverted',
        'invalid opcode: opcode 0xfe not defined',
        'Tried to read 32 bytes.  Only got 0 bytes',
        'error processing call Revert',
        'invalid opcode: INVALID',
    ]
    return any(trigger in str(e) for trigger in triggers)


def continue_if_call_reverted(e: Exception) -> None:
    if call_reverted(e): return
    else: raise e


def out_of_gas(e: Exception) -> bool:
    return 'out of gas' in str(e) 

# Provider Exceptions:

class NodeNotSynced(Exception):
    pass