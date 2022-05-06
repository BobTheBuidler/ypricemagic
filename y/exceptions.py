import logging
from brownie import Contract as BrownieContract
from brownie.exceptions import CompilerError
from y.utils.logging import yLazyLogger

logger = logging.getLogger(__name__)

# General

class NetworkNotSpecified(Exception):
    pass

class PriceError(Exception):
    pass

class UnsupportedNetwork(Exception):
    pass

class NonStandardERC20(Exception):
    pass

class CantFetchParam(Exception):
    pass


# Contracts

class ContractNotVerified(Exception):
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


@yLazyLogger(logger)
def contract_not_verified(e: Exception) -> bool:
    triggers = [
        'Contract source code not verified',
        'has not been verified',
    ]
    return any(trigger in str(e) for trigger in triggers)


# Pool detection

class NotAUniswapV2Pool(Exception):
    pass

class NotABalancerV2Pool(Exception):
    pass

# Uni

class CantFindSwapPath(Exception):
    pass

# Calls

class CalldataPreparationError(Exception):
    pass

class CallReverted(Exception):
    pass


@yLazyLogger(logger)
def call_reverted(e: Exception) -> bool:
    triggers = [
        'execution reverted',
        'No data was returned - the call likely reverted',
        'invalid opcode: opcode 0xfe not defined',
        'Tried to read 32 bytes.  Only got 0 bytes',
        'invalid jump destination',
        'error processing call Revert',
    ]
    return any(trigger in str(e) for trigger in triggers)


def continue_if_call_reverted(e: Exception) -> None:
    if call_reverted(e): return
    else: raise e


@yLazyLogger(logger)
def out_of_gas(e: Exception) -> bool:
    return 'out of gas' in str(e) 

# Provider Exceptions:

class NodeNotSynced(Exception):
    pass
