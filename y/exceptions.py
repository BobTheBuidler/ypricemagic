
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

def contract_not_verified(e: Exception) -> bool:
    triggers = [
        'Contract source code not verified',
        'has not been verified',
    ]
    return True if any(trigger in str(e) for trigger in triggers) not in str(e) else False