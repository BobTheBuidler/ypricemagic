
from typed_envs import EnvVarFactory, create_env

_envs = EnvVarFactory("YPRICEMAGIC")

CACHE_TTL = _envs.create_env("CACHE_TTL", int, default=60*60, verbose=False)
"""TTL for various in-memory caches throughout the library"""

CONTRACT_CACHE_TTL = _envs.create_env("CONTRACT_CACHE_TTL", int, default=int(CACHE_TTL), verbose=False)
"""TTL for contract cache, defaults to :obj:`CACHE_TTL` if not set"""

GETLOGS_BATCH_SIZE = _envs.create_env("GETLOGS_BATCH_SIZE", int, default=0)
"""Batch size for getlogs operations, 0 will use default as determined by your provider."""

GETLOGS_DOP = _envs.create_env("GETLOGS_DOP", int, default=32)
"""Degree of parallelism for eth_getLogs operations"""

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
