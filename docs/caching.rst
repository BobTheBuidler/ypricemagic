Caching in ypricemagic
======================

Overview
--------

ypricemagic uses multiple caching strategies to maximize performance, minimize redundant RPC/database calls, and provide fast access to frequently used data. This document describes the two main types of disk caches and the various in-memory LRU cache mechanisms used throughout the codebase.

Disk Caches
-----------

Local SQL Cache
~~~~~~~~~~~~~~~

- **Backend:** Pony ORM with SQLite (default, configurable via environment variables)
- **Location:** ``~/.ypricemagic/ypricemagic.sqlite`` (can be overridden with ``YPRICEMAGIC_SQLITE_PATH``)
- **Purpose:** Persistent storage for blockchain data, price data, and cache metadata.
- **What is cached:**
  - Blockchain data: chains, blocks, addresses, contracts, tokens, prices
  - Cache metadata: ``TraceCacheInfo``, ``LogCacheInfo`` (for logs/traces)
- **Implementation:** Entities defined in ``y/_db/entities.py``, setup in ``y/_db/config.py``
- **Usage:** Used for both persistent data and as a cache for expensive lookups.

Integration with eth-portfolio
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If [eth-portfolio](https://github.com/BobTheBuidler/eth-portfolio) is installed in your environment, ypricemagic will automatically use eth_portfolio's extended database schema and utility functions for persistent storage and lookups. This means:

- Both ypricemagic and eth_portfolio will share the same persistent SQL database (typically SQLite).
- Cached blockchain, price, and portfolio data will be unified and accessible to both packages.
- Utility functions such as `get_block` and `get_token` will use the eth_portfolio versions if available, ensuring consistent and extended data access.
- **No configuration is required:** the integration is seamless and automatic if eth_portfolio is present.

Joblib Disk Cache
~~~~~~~~~~~~~~~~~

- **Backend:** ``joblib.Memory``
- **Location:** ``cache/{chain.id}``
- **Purpose:** Disk-based function result caching for expensive or slow-to-compute results.
- **Usage:** Decorate functions with ``@memory.cache`` to persist results to disk.
- **Example:** Used in ``y/contracts.py`` and other modules.

Database Environment Variables
------------------------------

The following environment variables control how ypricemagic connects to and configures its database:

- **YPRICEMAGIC_DB_PROVIDER** (str, default: "sqlite"):  
  Database backend to use (e.g., "sqlite", "postgresql").

- **YPRICEMAGIC_SQLITE_PATH** (str, default: ``~/.ypricemagic/ypricemagic.sqlite``):  
  Path to the SQLite database file. Set this to use a custom or temporary database file (e.g., for testing, CI, or multiple environments).

- **YPRICEMAGIC_DB_HOST** (str, default: ""):  
  Host address for the database if not using sqlite.

- **YPRICEMAGIC_DB_PORT** (str, default: ""):  
  Port for the database.

- **YPRICEMAGIC_DB_USER** (str, default: ""):  
  Username for the database.

- **YPRICEMAGIC_DB_PASSWORD** (str, default: ""):  
  Password for the database.

- **YPRICEMAGIC_DB_DATABASE** (str, default: "ypricemagic"):  
  Database name.

Set these variables in your environment to control which database backend is used and how ypricemagic connects to it.

In-Memory LRU Caches
--------------------

Synchronous LRU Caches
~~~~~~~~~~~~~~~~~~~~~~

- **functools.lru_cache:** Used for pure in-memory caching of function results (e.g., token metadata, block lookups).
- **cachetools.cached/TTLCache:** Used for time-limited in-memory caching, especially for DB query results.
- **db_session_cached:** Combines ``lru_cache`` with DB session/retry logic for DB reads.

Asynchronous LRU Caches
~~~~~~~~~~~~~~~~~~~~~~~

- **async_lru.alru_cache:** Used for async LRU caching of coroutine results (e.g., async DB/API calls).
- **a_sync.a_sync:** Used for both sync and async function caching, with options for TTL and maxsize.
- **a_sync_ttl_cache:** Preconfigured async decorator with TTL, used for async memory caching.

What is LRU-cached
~~~~~~~~~~~~~~~~~~

- Token metadata (symbols, decimals, names, buckets)
- Contract ABIs and deploy blocks
- Block/timestamp lookups
- Price data
- Log topics and hashes
- Results of expensive on-chain or DB queries

Cache Control
~~~~~~~~~~~~~

- Many functions accept ``skip_cache`` parameters to force fresh computation.
- TTL and maxsize are configurable for many caches.
- Some caches are per-chain (partitioned by chain ID).

Summary Table
-------------

+-------------------+--------------------------+-----------------------------+-----------------------------+-------------+
| Cache Type        | Library/Decorator        | Example Usage               | What is Cached              | Sync/Async  |
+===================+==========================+=============================+=============================+=============+
| Local SQL         | Pony ORM (SQLite)        | y/_db/entities.py           | Blockchain data, cache meta | Sync        |
+-------------------+--------------------------+-----------------------------+-----------------------------+-------------+
| Joblib Disk       | joblib.Memory            | y/utils/cache.py,           | Function results            | Sync        |
|                   |                          | y/contracts.py              |                             |             |
+-------------------+--------------------------+-----------------------------+-----------------------------+-------------+
| LRU (in-memory)   | functools.lru_cache      | y/_db/utils/, y/contracts.py| Function results            | Sync        |
+-------------------+--------------------------+-----------------------------+-----------------------------+-------------+
| LRU (in-memory)   | cachetools.cached/TTL    | y/_db/utils/token.py        | DB query results            | Sync        |
+-------------------+--------------------------+-----------------------------+-----------------------------+-------------+
| LRU (in-memory)   | async_lru.alru_cache     | y/prices/utils/ypriceapi.py | Async function results      | Async       |
+-------------------+--------------------------+-----------------------------+-----------------------------+-------------+
| LRU (in-memory)   | a_sync.a_sync            | y/utils/cache.py,           | Sync/async function results | Sync/Async  |
|                   |                          | y/prices/yearn.py           |                             |             |
+-------------------+--------------------------+-----------------------------+-----------------------------+-------------+
| LRU (in-memory)   | db_session_cached        | y/_db/decorators.py         | DB reads                    | Sync        |
+-------------------+--------------------------+-----------------------------+-----------------------------+-------------+

References
----------

- ``y/utils/cache.py``
- ``y/_db/entities.py``
- ``y/_db/decorators.py``
- ``y/_db/utils/``
- ``y/contracts.py``
- ``y/prices/utils/ypriceapi.py``
