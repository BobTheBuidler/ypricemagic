
from typed_envs import EnvVarFactory, create_env

_envs = EnvVarFactory("YPRICEMAGIC")

# TTL for various in-memory caches thruout the library
CACHE_TTL = _envs.create_env("CACHE_TTL", int, default=60*60, verbose=False)
CONTRACT_CACHE_TTL = _envs.create_env("CONTRACT_CACHE_TTL", int, default=int(CACHE_TTL), verbose=False)

GETLOGS_BATCH_SIZE = _envs.create_env("GETLOGS_BATCH_SIZE", int, default=0)

DB_PROVIDER = _envs.create_env("DB_PROVIDER", str, default="sqlite", verbose=False)
DB_HOST = _envs.create_env("DB_HOST", str, default="", verbose=False)
DB_PORT = _envs.create_env("DB_PORT", str, default="", verbose=False)
DB_USER = _envs.create_env("DB_USER", str, default="", verbose=False)
DB_PASSWORD = _envs.create_env("DB_PASSWORD", str, default="", verbose=False)
DB_DATABASE = _envs.create_env("DB_DATABASE", str, default="ypricemagic", verbose=False)
SKIP_CACHE = _envs.create_env("SKIP_CACHE", bool, default=False, verbose=False)

# ypriceapi
SKIP_YPRICEAPI = create_env("SKIP_YPRICEAPI", bool, default=False, verbose=False)
