import asyncio
import logging
import os
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from itertools import zip_longest
from typing import Any, Dict, List, Optional

from brownie import chain, web3
from brownie.convert.datatypes import EthAddress
from brownie.network.event import EventDict, _decode_logs
from eth_typing import ChecksumAddress
from toolz import groupby
from web3.middleware.filter import block_ranges
from web3.types import LogReceipt
from y.contracts import contract_creation_block
from y.datatypes import Address, Block
from y.utils.cache import memory
from y.utils.middleware import BATCH_SIZE

from multicall.utils import await_awaitable, gather

logger = logging.getLogger(__name__)


def decode_logs(logs: List[LogReceipt]) -> EventDict:
    """
    Decode logs to events and enrich them with additional info.
    """
    decoded = _decode_logs(logs)
    for i, log in enumerate(logs):
        setattr(decoded[i], "block_number", log["blockNumber"])
        setattr(decoded[i], "transaction_hash", log["transactionHash"])
        setattr(decoded[i], "log_index", log["logIndex"])
    return decoded


def create_filter(address, topics=None):
    """
    Create a log filter for one or more contracts.
    Set fromBlock as the earliest creation block.
    """
    if isinstance(address, list):
        start_block = min(map(contract_creation_block, address))
    else:
        start_block = contract_creation_block(address)

    return web3.eth.filter({"address": address, "fromBlock": start_block, "topics": topics})


def get_logs_asap(address: Optional[Address], topics: Optional[List[str]], from_block: Optional[Block] = None, to_block: Optional[Block] = None, verbose: int = 0) -> List[Any]:
    return await_awaitable(
        get_logs_asap_async(address, topics, from_block=from_block, to_block=to_block, verbose=verbose)
    )

DOP = int(os.environ.get("DOP", 8))
thread_pool_executor = ThreadPoolExecutor(max_workers=DOP)

async def get_logs_asap_async(address: Optional[Address], topics: Optional[List[str]], from_block: Optional[Block] = None, to_block: Optional[Block] = None, verbose: int = 0) -> List[Any]:
    if from_block is None:
        from_block = 0 if address is None else contract_creation_block(address)
    if to_block is None:
        to_block = chain.height

    ranges = list(block_ranges(from_block, to_block, BATCH_SIZE))
    if verbose > 0:
        logger.info('fetching %d batches', len(ranges))
    
    batches = await gather([
        asyncio.get_event_loop().run_in_executor(
            thread_pool_executor,
            _get_logs,
            address,
            topics,
            start,
            end,
        )
        for start, end in ranges
    ])
    return [log for batch in batches for log in batch]

def logs_to_balance_checkpoints(logs) -> Dict[EthAddress,int]:
    """
    Convert Transfer logs to `{address: {from_block: balance}}` checkpoints.
    """
    balances = Counter()
    checkpoints = defaultdict(dict)
    for block, block_logs in groupby('blockNumber', logs).items():
        events = decode_logs(block_logs)
        for log in events:
            # ZERO_ADDRESS tracks -totalSupply
            sender, receiver, amount = log.values()  # there can be several different aliases
            balances[sender] -= amount
            checkpoints[sender][block] = balances[sender]
            balances[receiver] += amount
            checkpoints[receiver][block] = balances[receiver]
    return checkpoints


def checkpoints_to_weight(checkpoints, start_block: Block, end_block: Block) -> float:
    total = 0
    for a, b in zip_longest(list(checkpoints), list(checkpoints)[1:]):
        if a < start_block or a > end_block:
            continue
        b = min(b, end_block) if b else end_block
        total += checkpoints[a] * (b - a) / (end_block - start_block)
    return total

def _get_logs(
    address: Optional[ChecksumAddress],
    topics: Optional[List[str]],
    start: Block,
    end: Block
    ) -> List[LogReceipt]:
    if end - start == BATCH_SIZE - 1:
        response = _get_logs_batch_cached(address, topics, start, end)
    else:
        response = _get_logs_no_cache(address, topics, start, end)
    for log in response:
        if log.address != address:
            ''' I have this due to a corrupt cache on my local box that I would prefer not to lose. '''
            ''' It will not impact your scripts. ''' 
            response.remove(log)
    return response


def _get_logs_no_cache(
    address: Optional[ChecksumAddress],
    topics: Optional[List[str]],
    start: Block,
    end: Block
    ) -> List[LogReceipt]:
    logger.debug(f'fetching logs {start} to {end}')
    try:
        if address is None:
            response = web3.eth.get_logs({"topics": topics, "fromBlock": start, "toBlock": end})
        elif topics is None:
            response = web3.eth.get_logs({"address": address, "fromBlock": start, "toBlock": end})
        else:
            response = web3.eth.get_logs({"address": address, "topics": topics, "fromBlock": start, "toBlock": end})
    except Exception as e:
        errs = [
            "Service Unavailable for url:",
            "exceed maximum block range",
            "block range is too wide",
        ]
        if any(err in str(e) for err in errs):
            logger.debug('your node is having trouble, breaking batch in half')
            batch_size = (end - start + 1)
            half_of_batch = batch_size // 2
            batch1_end = start + half_of_batch
            batch2_start = batch1_end + 1
            batch1 = _get_logs_no_cache(address, topics, start, batch1_end)
            batch2 = _get_logs_no_cache(address, topics, batch2_start, end)
            response = batch1 + batch2
        else:
            raise
    return response



##############################
# Leaving this here so as to not upset people's caches
##############################


@memory.cache()
def _get_logs_batch_cached(
    address: Optional[str],
    topics: Optional[List[str]],
    start: Block,
    end: Block
    ) -> List[LogReceipt]:
    return _get_logs_no_cache(address, topics, start, end)
