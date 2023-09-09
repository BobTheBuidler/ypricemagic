
from typed_envs import EnvVarFactory

_envs = EnvVarFactory("YPRICEMAGIC")

# TTL for various in-memory caches thruout the library
CACHE_TTL = _envs.create_env("CACHE_TTL", int, default=60*60, verbose=False)
CONTRACT_CACHE_TTL = _envs.create_env("CONTRACT_CACHE_TTL", int, default=int(CACHE_TTL), verbose=False)

DB_PROVIDER = _envs.create_env("DB_PROVIDER", str, default="sqlite", verbose=False)
DB_HOST = _envs.create_env("DB_HOST", str, default="", verbose=False)
DB_USER = _envs.create_env("CACHE_TTL", str, default="", verbose=False)
DB_PASSWORD = _envs.create_env("CACHE_TTL", str, default="", verbose=False)
DB_DATABASE = _envs.create_env("CACHE_TTL", str, default="ypricemagic", verbose=False)
