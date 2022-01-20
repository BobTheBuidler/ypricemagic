
class PriceError(Exception):
    pass

class UnsupportedNetwork(Exception):
    pass

class NonStandardERC20(Exception):
    pass

class NotUniswapPoolV2(Exception):
    pass

class CalldataPreparationError(Exception):
    pass

class ContractNotVerified(Exception):
    pass

class CallReverted(Exception):
    pass


def contract_not_verified(e: Exception) -> bool:
    triggers = [
        'Contract source code not verified',
        'has not been verified',
    ]
    return any(trigger in str(e) for trigger in triggers)


def call_reverted(e: Exception) -> bool:
    triggers = [
        'execution reverted',
        'No data was returned - the call likely reverted',
    ]
    return any(trigger in str(e) for trigger in triggers)


def continue_if_call_reverted(e: Exception) -> None:
    if call_reverted(e): return
    else: raise e
    