from decimal import Decimal
from typing import Optional

from a_sync import a_sync
from dank_mids.exceptions import Revert
from multicall.call import Call

from y import ENVIRONMENT_VARIABLES as ENVS
from y.classes.common import ERC20, WeiBalance
from y.contracts import Contract, has_methods
from y.datatypes import Address, Block
from y.utils.cache import optional_async_diskcache


METHODS = "main()(address)", "issuanceAvailable()(uint)", "redemptionAvailable()(uint)"


@a_sync(default="sync")
@optional_async_diskcache
async def is_rtoken(token_address: Address) -> bool:
    """
    Determine whether a given token is a Reserve Protocol R-token.

    Args:
        token_address: The address of the token to check.

    Returns:
        True if the token is a Reserve Protocol R-token, False otherwise.

    Example:
        >>> address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"  # USDC (not an R-token)
        >>> result = is_rtoken(address)
        >>> print(result)
        False

    See Also:
        :func:`~y.prices.tokenized_fund.reserve.get_price`
    """
    return await has_methods(token_address, METHODS, sync=False)


@a_sync(default="sync")
async def get_price(
    token_address: Address,
    block: Optional[Block] = None,
    skip_cache: bool = ENVS.SKIP_CACHE,
) -> Decimal:
    """
    Retrieve the USD price of a Reserve Protocol R-token.

    This function obtains the basket handler associated with the R-token by calling its
    "main" and "basketHandler" methods. It then calls the basket handler's price method to retrieve a
    low and a high price value. The function computes the integer average of these two price values and scales
    the result by 1e18 to convert it to a USD price. If the call to the basket handler's price method reverts,
    the function returns None instead of raising an exception.

    Args:
        token_address: The address of the R-token.
        block: The block number to query. Defaults to the latest block if not specified.
        skip_cache: If True, skip using the cache. Defaults to :attr:`~y.ENVIRONMENT_VARIABLES.SKIP_CACHE`.

    Returns:
        The USD price of the R-token as computed from the basket handler, or None if the price cannot
        be determined due to a remote call failure (i.e. a :class:`~dank_mids.exceptions.Revert`).

    Raises:
        TypeError: If the token is not a valid R-token.

    Example:
        >>> address = "0xaCeeD87BD5754c3d714F3Bd43a9B7B0C9250ab0D"  # RSV token
        >>> price = await get_price(address, sync=False)
        >>> if price is None:
        ...     print("Price calculation failed due to a Revert exception")
        ... else:
        ...     print(f"Calculated price: {price}")
        >>> # In a synchronous context:
        >>> price = get_price(address)
        >>> print(price)

    See Also:
        :func:`~y.prices.tokenized_fund.reserve.is_rtoken`
    """
    main = await Call(token_address, "main()(address)", block_id=block)
    if main is None:
        raise TypeError(main, token_address, await is_rtoken(token_address, sync=False))
    basket_handler = await Contract.coroutine(
        await Call(main, "basketHandler()(address)", block_id=block)
    )
    try:
        low, high = await basket_handler.price.coroutine(block_identifier=block)
    except Revert:
        return None
    else:
        return Decimal(low + high) // 2 / 10**18

    tokens, *_ = await basket_handler.getPrimeBasket.coroutine(block_identifier=block)
    tokens = [ERC20(token, asynchronous=True) for token in tokens]
    balances = [
        WeiBalance(balance, token, block=block, skip_cache=skip_cache, asynchronous=True)
        for token, balance in zip(
            tokens, await basket_handler.quantity.map(tokens, block_identifier=block)
        )
    ]
    print(balances)
    values = WeiBalance.value_usd.map(balances).values()
    print(values)
    value = sum(values)
    print(value)
    supply = await ERC20(token_address, asynchronous=True).total_supply_readable(block)
    print(f"ts: {supply}")
    raise Exception(value / supply)
