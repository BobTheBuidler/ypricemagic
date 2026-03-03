# Caching

Cache migration patterns, cachebox API reference, and migration decisions.

**What belongs here:** cachebox usage patterns, migration gotchas, env var names for cache sizes.

---

## cachebox Quick Reference

```python
import cachebox

# LRU cache (thread-safe, bounded)
@cachebox.cached(cachebox.LRUCache(maxsize))
def my_func(arg):
    ...

# TTL cache (thread-safe, bounded, time-based expiry)
@cachebox.cached(cachebox.TTLCache(maxsize, ttl=seconds))
def my_func(arg):
    ...

# Works on async too
@cachebox.cached(cachebox.LRUCache(maxsize))
async def my_async_func(arg):
    ...

# Direct cache usage (dict-like)
cache = cachebox.LRUCache(1000)
cache["key"] = "value"
cache.get("key")
len(cache)
```

## Migration Patterns

| Before | After |
|--------|-------|
| `@lru_cache(maxsize=None)` | `@cachebox.cached(cachebox.LRUCache(ENVS.X))` |
| `@lru_cache(maxsize=128)` | `@cachebox.cached(cachebox.LRUCache(128))` |
| `@cached(TTLCache(N, ttl=T), lock=Lock())` | `@cachebox.cached(cachebox.TTLCache(N, ttl=T))` |
| `@ttl_cache(maxsize=N, ttl=T)` | `@cachebox.cached(cachebox.TTLCache(N, ttl=T))` |
| `@alru_cache(maxsize=N, ttl=T)` | `@cachebox.cached(cachebox.TTLCache(N, ttl=T))` |
| `@alru_cache(maxsize=N)` | `@cachebox.cached(cachebox.LRUCache(N))` |
| `@a_sync(cache_type="memory")` | Add `ram_cache_maxsize=ENVS.X` (DO NOT replace) |

## a_sync Cache Bounding

For `@a_sync` decorators, do NOT replace with cachebox. Just add the `ram_cache_maxsize` parameter:

```python
# Before
@a_sync(cache_type="memory", ram_cache_ttl=ENVS.CACHE_TTL)
async def _get_price(token, block):
    ...

# After
@a_sync(cache_type="memory", ram_cache_ttl=ENVS.CACHE_TTL, ram_cache_maxsize=ENVS.PRICE_CACHE_MAXSIZE)
async def _get_price(token, block):
    ...
```
