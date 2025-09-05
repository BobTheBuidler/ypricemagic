import asyncpg
import os

_asyncpg_pool = None


async def get_asyncpg_pool():
    """
    Get or create a global asyncpg connection pool using environment/config variables.
    """
    global _asyncpg_pool
    if _asyncpg_pool is None:
        db_host = os.environ.get("DB_HOST", "localhost")
        db_port = int(os.environ.get("DB_PORT", 5432))
        db_user = os.environ.get("DB_USER", "postgres")
        db_password = os.environ.get("DB_PASSWORD", "")
        db_database = os.environ.get("DB_DATABASE", "ypricemagic")
        _asyncpg_pool = await asyncpg.create_pool(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_database,
            min_size=1,
            max_size=10,
        )
    return _asyncpg_pool
