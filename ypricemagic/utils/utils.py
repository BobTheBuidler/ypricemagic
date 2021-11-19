import datetime
import logging

from brownie import Contract, chain, web3
from cachetools.func import lru_cache

import ypricemagic.utils.events
from .cache import memory
from ..interfaces.ERC20 import ERC20ABI
from ..constants import PROXIES

logger = logging.getLogger(__name__)

@lru_cache(1)
def get_ethereum_client():
    client = web3.clientVersion
    if client.startswith('TurboGeth'):
        return 'tg'
    if client.lower().startswith('erigon'):
        return 'erigon'
    if client.lower().startswith('geth'):
        return 'geth'
    logging.debug(f"client: {client}")
    return client


def safe_views(abi):
    return [
        item["name"]
        for item in abi
        if item["type"] == "function"
        and item["stateMutability"] == "view"
        and not item["inputs"]
        and all(x["type"] in ["uint256", "bool"] for x in item["outputs"])
    ]


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
def closest_block_after_timestamp(timestamp):
    logger.info('closest block after timestamp %d', timestamp)
    height = chain.height
    lo, hi = 0, height
    while hi - lo > 1:
        mid = lo + (hi - lo) // 2
        if get_block_timestamp(mid) > timestamp:
            hi = mid
        else:
            lo = mid
    return hi if hi != height else None
    

@memory.cache()
def contract_creation_block(address) -> int:
    """
    Determine the block when a contract was created.
    """
    logger.info("contract creation block %s", address)
    # NOTE: Testing to see if we even need this, will likely remove later
    #client = get_ethereum_client()
    #if client in ['tg', 'erigon', 'geth']:
    return _contract_creation_block_binary_search(address)
    #else:
    #    return _contract_creation_block_bigquery(address)


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

@lru_cache
def get_decimals_with_override(address, block=None):
    try:
        return DECIMAL_OVERRIDES[str(address)]
    except KeyError:
        try:
            return Contract(address).decimals()
        except (AttributeError, ValueError):
            try:
                return Contract(address).DECIMALS()
            except (AttributeError, ValueError): # NOTE: if AttributeError, 'address' is a proxy and we need to look at the implementation
                if is_AdminUpgradeabilityProxy(address):
                    topics = [web3.keccak(text='Upgraded(address)').hex()]
                    upgrade_events = ypricemagic.utils.events.get_logs_asap(address, topics, to_block=block)
                    try: # NOTE: for debugging purposes only
                        current = max(event.blockNumber for event in upgrade_events)
                    except:
                        raise
                    event = [event for event in upgrade_events if event.blockNumber == current]
                    implementation = ypricemagic.utils.events.decode_logs(event)['Upgraded']['implementation']
                    return Contract(implementation).decimals()
                elif is_PProxy(address):
                    return Contract(Contract(address).getImplementation()).decimals()
                else: # NOTE: This will throw
                    return Contract_erc20(address).decimals()        

def PROXIES_reverse_lookup(token):
    try:
        return [key for key, value in PROXIES.items() if value == token][0]
    except IndexError:
        return token

def is_AdminUpgradeabilityProxy(address):
    required = {"upgradeTo", "upgradeToAndCall", "implementation", "changeAdmin", "admin"}
    return set(Contract(address).__dict__) & required == required

def is_PProxy(address):
    required = {"getImplementation"}
    return set(Contract(address).__dict__) & required == required

if chain.id == 1:
    DECIMAL_OVERRIDES = {
        '0x88df592f8eb5d7bd38bfef7deb0fbc02cf3778a0': 18
        ,'0x78F225869c08d478c34e5f645d07A87d3fe8eb78': 18
        ,'0x17525E4f4Af59fbc29551bC4eCe6AB60Ed49CE31': 18
        ,'0x79A91cCaaa6069A571f0a3FA6eD257796Ddd0eB4': 18
        ,'0x043942281890d4876D26BD98E2BB3F662635DFfb': 10
        ,'0x33e18a092a93ff21aD04746c7Da12e35D34DC7C4': 18
        ,'0x0Ba45A8b5d5575935B8158a88C631E9F9C95a2e5': 18
        ,'0xE0B7927c4aF23765Cb51314A0E0521A9645F0E2A': 9
        ,'0x9A48BD0EC040ea4f1D3147C025cd4076A2e71e3e': 18
        ,'0x57Ab1E02fEE23774580C119740129eAC7081e9D3': 18
    }
elif chain.id == 56: # bsc
    DECIMAL_OVERRIDES = {
        '0xf859Bf77cBe8699013d6Dbc7C2b926Aaf307F830': 18
    }
elif chain.id == 137: # poly
    DECIMAL_OVERRIDES = {
        '0xe6FC6C7CB6d2c31b359A49A33eF08aB87F4dE7CE': 6
        ,'0x2a93172c8DCCbfBC60a39d56183B7279a2F647b4': 18
        ,'0x9f5755D47fB80100E7ee65Bf7e136FCA85Dd9334': 18
    }
elif chain.id == 250:
    DECIMAL_OVERRIDES = {

    }

def Contract_with_erc20_fallback(address):
    try:
        contract = Contract(address)
    except (AttributeError, ValueError, IndexError):
        contract = Contract_erc20(address)
    return contract

def Contract_erc20(address):
    return Contract.from_abi('ERC20',address,ERC20ABI)