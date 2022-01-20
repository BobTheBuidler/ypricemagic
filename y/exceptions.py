
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
    message = 'Contract source code not verified'
    return True if message not in str(e) else False