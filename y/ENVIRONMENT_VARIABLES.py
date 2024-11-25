from a_sync import PruningThreadPoolExecutor
from typed_envs import EnvVarFactory, create_env

_envs = EnvVarFactory("YPRICEMAGIC")

CACHE_TTL = _envs.create_env("CACHE_TTL", int, default=60 * 60, verbose=False)
"""TTL for various in-memory caches throughout the library"""

CONTRACT_CACHE_TTL = _envs.create_env(
    "CONTRACT_CACHE_TTL", int, default=int(CACHE_TTL), verbose=False
)
"""TTL for contract cache, defaults to :obj:`CACHE_TTL` if not set"""

CONTRACT_THREADS = _envs.create_env(
    "CONTRACT_THREADS",
    PruningThreadPoolExecutor,
    default=10,
    string_converter=int,
    verbose=False,
)
"""The number of threads to use to fetch contract abis"""

GETLOGS_BATCH_SIZE = _envs.create_env("GETLOGS_BATCH_SIZE", int, default=0)
"""Batch size for getlogs operations, 0 will use default as determined by your provider."""

GETLOGS_DOP = _envs.create_env("GETLOGS_DOP", int, default=32, verbose=False)
"""Degree of parallelism for eth_getLogs operations"""

CHECKSUM_CACHE_MAXSIZE = _envs.create_env(
    "CHECKSUM_CACHE_MAXSIZE", int, default=100_000, verbose=False
)
"""The maximum number of lru-cached keys kept in the checksum cache."""

DB_PROVIDER = _envs.create_env("DB_PROVIDER", str, default="sqlite", verbose=False)
"""Database provider (e.g., 'sqlite', 'postgresql')"""

DB_HOST = _envs.create_env("DB_HOST", str, default="", verbose=False)
"""Database host address"""

DB_PORT = _envs.create_env("DB_PORT", str, default="", verbose=False)
"""Database port number"""

DB_USER = _envs.create_env("DB_USER", str, default="", verbose=False)
"""Database user name"""

DB_PASSWORD = _envs.create_env("DB_PASSWORD", str, default="", verbose=False)
"""Database password"""

DB_DATABASE = _envs.create_env("DB_DATABASE", str, default="ypricemagic", verbose=False)
"""Database name"""

SKIP_CACHE = _envs.create_env("SKIP_CACHE", bool, default=False, verbose=False)
"""Flag to skip cache usage"""

# ypriceapi
SKIP_YPRICEAPI = create_env("SKIP_YPRICEAPI", bool, default=False, verbose=False)
"""Flag to skip using ypriceapi"""
