
from decimal import Decimal
from typing import Optional

from a_sync import a_sync
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
    return await has_methods(token_address, METHODS, sync=False)

@a_sync(default="sync")
async def get_price(token_address: Address, block: Optional[Block] = None, skip_cache: bool = ENVS.SKIP_CACHE) -> Decimal:
    main = await Call(token_address, "main()(address)", block_id=block)
    if main is None:
        raise TypeError(main, token_address, await is_rtoken(token_address))
    basket_handler = await Contract.coroutine(await Call(main, "basketHandler()(address)", block_id=block))
    low, high = await basket_handler.price.coroutine(block_identifier=block)
    return Decimal(low + high) // 2 / 10 ** 18
    tokens, *_ = await basket_handler.getPrimeBasket.coroutine(block_identifier=block)
    tokens = [ERC20(token, asynchronous=True) for token in tokens]
    balances = [
        WeiBalance(balance, token, block=block, skip_cache=skip_cache, asynchronous=True)
        for token, balance
        in zip(tokens, await basket_handler.quantity.map(tokens, block_identifier=block))
    ]
    print(balances)
    values = WeiBalance.value_usd.map(balances).values()
    print(values)
    value = sum(values)
    print(value)
    supply = await ERC20(token_address, asynchronous=True).total_supply_readable(block)
    print(f'ts: {supply}')
    raise Exception(value / supply)

