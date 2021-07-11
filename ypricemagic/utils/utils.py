import logging, datetime
from brownie import chain, web3
from cachetools.func import lru_cache
from .cache import memory

logger = logging.getLogger(__name__)

@lru_cache(1)
def get_ethereum_client():
    client = web3.clientVersion
    if client.startswith('TurboGeth'):
        return 'tg'
    if client.startswith('Erigon'):
        return 'erigon'
    return client

@memory.cache() 
def get_block_timestamp(height):
    client = get_ethereum_client()
    if client in ['tg', 'erigon']:
        header = web3.manager.request_blocking(f"{client}_getHeaderByNumber", [height])
        return int(header.timestamp, 16)
    else:
        return chain[height].timestamp


@memory.cache() 
def last_block_on_date(date_string):
    logger.debug('last block on date %d', date_string)
    date = datetime.datetime.strptime(date_string, "%Y-%m-%d")
    date = date.date()
    height = chain.height
    lo, hi = 0, height
    while hi - lo > 1:
        mid = lo + (hi - lo) // 2
        logger.debug('block: ' + str(mid))
        logger.debug('mid: ' + str(datetime.date.fromtimestamp(get_block_timestamp(mid))))
        logger.debug(date)
        if datetime.date.fromtimestamp(get_block_timestamp(mid)) > date:
            hi = mid
        else:
            lo = mid
    hi = hi - 1
    return hi if hi != height else None

@memory.cache()
def contract_creation_block(address) -> int:
    """
    Determine the block when a contract was created.
    """
    logger.info("contract creation block %s", address)
    client = get_ethereum_client()
    if client in ['tg', 'erigon']:
        return _contract_creation_block_binary_search(address)
    else:
        return _contract_creation_block_bigquery(address)


def _contract_creation_block_binary_search(address):
    """
    Find contract creation block using binary search.
    NOTE Requires access to historical state. Doesn't account for CREATE2 or SELFDESTRUCT.
    """
    height = chain.height
    lo, hi = 0, height
    while hi - lo > 1:
        mid = lo + (hi - lo) // 2
        if web3.eth.get_code(address, block_identifier=mid):
            hi = mid
        else:
            lo = mid
    return hi if hi != height else None


def _contract_creation_block_bigquery(address):
    """
    Query contract creation block using BigQuery.
    NOTE Requires GOOGLE_APPLICATION_CREDENTIALS
         https://cloud.google.com/bigquery/docs/quickstarts/quickstart-client-libraries
    """
    from google.cloud import bigquery

    client = bigquery.Client()
    query = "select block_number from `bigquery-public-data.crypto_ethereum.contracts` where address = @address limit 1"
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("address", "STRING", address.lower())]
    )
    query_job = client.query(query, job_config=job_config)
    for row in query_job:
        return row["block_number"]