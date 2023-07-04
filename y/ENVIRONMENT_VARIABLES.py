
from typed_envs import EnvVarFactory

_envs = EnvVarFactory("YPRICEMAGIC")

# TTL for various in-memory caches thruout the library
CACHE_TTL = _envs.create_env("CACHE_TTL", int, default=60*60, verbose=False)
