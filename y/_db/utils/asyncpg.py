import asyncio
from typing import Final, Optional

import asyncpg

import y._db.config as db_config


POOL_LOCK: Final = asyncio.Lock()
_asyncpg_pool: asyncpg.Pool | None = None


async def set_asyncpg_pool() -> asyncpg.Pool:
    global _asyncpg_pool
    _asyncpg_pool = await asyncpg.create_pool(
        host=db_config.connection_settings["host"],
        user=db_config.connection_settings["user"],
        password=db_config.connection_settings["password"],
        database=db_config.connection_settings["database"],
        port=db_config.connection_settings.get("port", 5432),
        min_size=1,
        max_size=10,
    )
    return _asyncpg_pool


async def get_asyncpg_pool() -> asyncpg.Pool:
    # sourcery skip: assign-if-exp, reintroduce-else
    async with POOL_LOCK:
        if _asyncpg_pool is not None:
            return _asyncpg_pool
        return await set_asyncpg_pool()
