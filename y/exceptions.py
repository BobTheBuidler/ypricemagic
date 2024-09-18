import logging
from typing import TYPE_CHECKING, Any, Optional

from brownie import Contract as BrownieContract
from brownie.exceptions import CompilerError
from web3.exceptions import ContractLogicError

from y.datatypes import AnyAddressType

if TYPE_CHECKING:
    from y.prices.dex.uniswap.v2 import UniswapV2Pool

logger = logging.getLogger(__name__)

# General

class yPriceMagicError(ValueError):
    """
    Custom exception for ypricemagic-related errors.

    This exception is raised when any error occurs inside of ypricemagic.
    For example, if a price fails to fetch or if there are unexpected 
    Exceptions while calculating prices.
    """

    def __init__(self, exc: Exception, token: str, block: Optional[int], symbol: str):
        self.token = token
        """
        The token that caused the error.
        """

        self.block = block
        """
        The block that was queried when the error occurred.
        """

        self.exception = exc
        """
        The original :class:`~Exception` that was raised and wrapped with the yPriceMagicError.
        """

        detail = exc.__class__.__name__
        if not isinstance(self.exception, PriceError):
            detail += f'({exc})'
        # We do the import here to avoid a circular dependency
        from y import Network
        super().__init__(f"{detail} while fetching {Network.printable()} {symbol} {address} at block {block}")

class PriceError(Exception):
    """
    Raised when a queried price is not found.
    """

    def __init__(self, logger: logging.Logger, symbol: str):
        super().__init__(f"No price found for {symbol} {logger.address} at block {logger.block}")

class UnsupportedNetwork(ValueError):
    """
    Raised when an operation is attempted on an unsupported blockchain network.
    """

class NonStandardERC20(Exception):
    """
    Raised when an ERC20 token contract is expected but the provided address is not a standard ERC20 token.
    """

class CantFetchParam(Exception):
    pass


class TokenError(ValueError):
    """Raised when a token contract is not the correct contract type for the desired operation."""
    def __init__(self, token: AnyAddressType, desired_type: str, *optional_extra_args: Any):
        super().__init__(f"{token} is not a {desired_type}", *optional_extra_args)

# Explorer Exceptions

class _ExplorerError(Exception):
    """
    Base class for exceptions related to block explorer interactions.

    These errors are specific to issues encountered when interacting with blockchain explorers like Etherscan.
    """

class InvalidAPIKeyError(_ExplorerError):
    """
    Raised when the API key for the block explorer has been rejected.
    This typically occurs when making requests to a block explorer API with a missing, incorrect, or banned key.
    """
    _msg = "The block explorer for this network says your API key is invalid."
    def __init__(self, msg: str = ''):
        super().__init__(msg or self._msg)

# Contracts

class ContractNotVerified(_ExplorerError):
    """
    Raised when attempting to fetch the ABI for an unverified contract from a block explorer.
    """

class NoProxyImplementation(Exception):
    """
    Raised when the implementation address of a proxy contract cannot be determined.

    This may occur when trying to interact with proxy contracts that don't follow standard patterns.
    """

class MessedUpBrownieContract(Exception):
    """
    Raised when there's an issue initialized a Brownie contract instance,
    typically in the compilation step.
    """

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
    """
    Raised when a contract is incorrectly identified as a Uniswap V2 pool.
    """
    # NOTE: we use this exc to get the non-pool out of the pool singleton so it doesn't grow forever
    # TODO: Refactor this goofy thing out
    def __init__(self, non_pool: "UniswapV2Pool"):
        from y.prices.dex.uniswap.v2 import UniswapV2Pool
        UniswapV2Pool._ChecksumASyncSingletonMeta__instances[True].pop(non_pool.address, None)
        UniswapV2Pool._ChecksumASyncSingletonMeta__instances[False].pop(non_pool.address, None)
        super().__init__(non_pool.address)

class NotABalancerV2Pool(Exception):
    """
    Raised when a contract is incorrectly identified as a Balancer V2 pool.
    """

# Uni

class CantFindSwapPath(Exception):
    pass

class TokenNotFound(ValueError):
    """
    Raised when a specified token cannot be found in a given container.

    This is usually used when searching for a token in a liquidity pool.
    """
    
    def __init__(self, token, container):
        super().__init__(f"{token} is not in {container}")

# Calls

class CalldataPreparationError(Exception):
    """
    Raised when there's an error in preparing calldata for a contract interaction.
    """

class CallReverted(Exception):
    """
    Raised when a contract call is reverted.
    """


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