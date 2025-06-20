from os import path
from typing import Final

from typed_envs import EnvVarFactory, create_env


_envs: Final = EnvVarFactory("YPRICEMAGIC")

CACHE_TTL: Final = _envs.create_env("CACHE_TTL", int, default=60 * 60, verbose=False)
"""TTL for various in-memory caches throughout the library"""

CONTRACT_CACHE_TTL: Final = _envs.create_env(
    "CONTRACT_CACHE_TTL", int, default=int(CACHE_TTL), verbose=False
)
"""TTL for contract cache, defaults to :obj:`CACHE_TTL` if not set"""

GETLOGS_BATCH_SIZE: Final = _envs.create_env("GETLOGS_BATCH_SIZE", int, default=0)
"""Batch size for getlogs operations, 0 will use default as determined by your provider."""

GETLOGS_DOP: Final = _envs.create_env("GETLOGS_DOP", int, default=32, verbose=False)
"""Degree of parallelism for eth_getLogs operations"""

CHECKSUM_CACHE_MAXSIZE: Final = _envs.create_env(
    "CHECKSUM_CACHE_MAXSIZE", int, default=100_000, verbose=False
)
"""The maximum number of lru-cached keys kept in the checksum cache."""

DB_PROVIDER: Final = _envs.create_env("DB_PROVIDER", str, default="sqlite", verbose=False)
"""Database provider (e.g., 'sqlite', 'postgresql')"""

SQLITE_PATH: Final = _envs.create_env(
    "SQLITE_PATH",
    str,
    default=f"{path.expanduser('~')}/.ypricemagic/ypricemagic.sqlite",
    verbose=False,
)
"""
Path to the SQLite database file if :obj:`~DB_PROVIDER` is "sqlite".

By default, this is ``~/.ypricemagic/ypricemagic.sqlite``.

This env is useful for testing, CI, or running multiple isolated environments.
"""

DB_HOST: Final = _envs.create_env("DB_HOST", str, default="", verbose=False)
"""Database host address if :data:`~DB_PROVIDER` is not "sqlite"."""

DB_PORT: Final = _envs.create_env("DB_PORT", str, default="", verbose=False)
"""Database port number"""

DB_USER: Final = _envs.create_env("DB_USER", str, default="", verbose=False)
"""Database user name"""

DB_PASSWORD: Final = _envs.create_env("DB_PASSWORD", str, default="", verbose=False)
"""Database password"""

DB_DATABASE: Final = _envs.create_env("DB_DATABASE", str, default="ypricemagic", verbose=False)
"""Database name"""

SKIP_CACHE: Final = _envs.create_env("SKIP_CACHE", bool, default=False, verbose=False)
"""Flag to skip cache usage"""

# ypriceapi
SKIP_YPRICEAPI: Final = create_env("SKIP_YPRICEAPI", bool, default=False, verbose=False)
"""Flag to skip using ypriceapi"""
