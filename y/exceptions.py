import logging
from brownie import Contract
from y.decorators import log

logger = logging.getLogger(__name__)

# General

class PriceError(Exception):
    pass

class UnsupportedNetwork(Exception):
    pass

class NonStandardERC20(Exception):
    pass


# Contracts

class ContractNotVerified(Exception):
    pass

class MessedUpBrownieContract(Exception):
    def __init__(self, address, *args: object) -> None:
        super().__init__(*args)
        # try to recache the contract
        Contract.from_explorer(address)


@log(logger)
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


# Calls

class CalldataPreparationError(Exception):
    pass

class CallReverted(Exception):
    pass


@log(logger)
def call_reverted(e: Exception) -> bool:
    triggers = [
        'execution reverted',
        'No data was returned - the call likely reverted',
        'invalid opcode: opcode 0xfe not defined',
        'Tried to read 32 bytes.  Only got 0 bytes',
        'invalid jump destination'
    ]
    return any(trigger in str(e) for trigger in triggers)


def continue_if_call_reverted(e: Exception) -> None:
    if call_reverted(e): return
    else: raise e


@log(logger)
def out_of_gas(e: Exception) -> bool:
    return 'out of gas' in str(e) 
