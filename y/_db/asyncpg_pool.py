import asyncpg
import os

from async_lru import alru_cache


@alru_cache(maxsize=None)
async def get_asyncpg_pool() -> asyncpg.Pool:
    """
    Get or create a global asyncpg connection pool using environment/config variables.
    """
    return await asyncpg.create_pool(
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", 5432)),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_DATABASE", "ypricemagic"),
        min_size=1,
        max_size=10,
    )
