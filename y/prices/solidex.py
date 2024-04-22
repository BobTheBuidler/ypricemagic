
from typing import Optional

import a_sync
from async_lru import alru_cache
from brownie import chain
from brownie.convert.datatypes import EthAddress

from y import ENVIRONMENT_VARIABLES as ENVS
from y.classes.common import ERC20
from y.contracts import Contract
from y.datatypes import AnyAddressType
from y.networks import Network
from y.prices import magic
from y.exceptions import ContractNotVerified
from brownie.exceptions import ContractNotFound


@a_sync.a_sync(default='sync')
async def is_solidex_deposit(token: AnyAddressType) -> bool:
    if chain.id != Network.Fantom:
        return False
    try:
        contract = await Contract.coroutine(token)
    except (ContractNotVerified, ContractNotFound):
        return False
    if not hasattr(contract, 'pool'):
        return False
    name = await ERC20(token, asynchronous=True).name
    return name.startswith("Solidex") and name.endswith("Deposit")

@a_sync.a_sync(default='sync')
async def get_price(token: AnyAddressType, block: Optional[int] = None, skip_cache: bool = ENVS.SKIP_CACHE):
    pool = await _get_pool(token)
    return await magic.get_price(pool, block, skip_cache=skip_cache, sync=False)

@alru_cache(maxsize=None)
async def _get_pool(token) -> EthAddress:
    contract = await Contract.coroutine(token)
    return await contract.pool