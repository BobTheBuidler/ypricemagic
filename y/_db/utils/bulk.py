
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Iterable
from pony.orm import Database, DatabaseError

from y._db import entities
from y._db.decorators import a_sync_write_db_session


logger = logging.getLogger(__name__)

def execute(sql: str, *, db: Database = entities.db) -> None:
    try:
        logger.debug("EXECUTING SQL")
        logger.debug(sql)
        db.execute(sql)
    except DatabaseError as e:
        logger.warning("%s %s when executing SQL`%s`", e.__class__.__name__, e, sql)
        raise ValueError(e, sql) from e

def stringify_column_value(value: Any, provider: str) -> str:
    if value is None:
        return 'null'
    elif isinstance(value, bytes):
        if provider == 'postgres':
            #return f"E'\\x{value.hex()}"
            return f"'{value.decode()}'::bytea"
        elif provider == 'sqlite':
            return f"X'{value.hex()}'"
        raise NotImplementedError(provider)
    elif isinstance(value, str):
        return f"'{value}'"
    elif isinstance(value, (int, Decimal)):
        return str(value)
    elif isinstance(value, datetime):
        return f"'{value.astimezone(timezone.utc).isoformat()}'"
    else:
        raise NotImplementedError(type(value), value)
        
def build_row(row: Iterable[Any], provider: str) -> str:
    return f"({','.join(stringify_column_value(col, provider) for col in row)})"

@a_sync_write_db_session
def insert(
    entity_type: entities.db.Entity, 
    columns: Iterable[str], 
    items: Iterable[Iterable[Any]],
    *,
    db: Database = entities.db,
) -> None:
    data = ",".join(build_row(i, db.provider_name) for i in items)
    if db.provider_name == 'sqlite':
        execute(f'insert or ignore into {entity_type.__name__.lower()} ({",".join(columns)}) values {data}', db=db)
    elif db.provider_name == 'postgres':
        execute(f'insert into {entity_type.__name__.lower()} ({",".join(columns)}) values {data} on conflict do nothing', db=db)
    else:
        raise NotImplementedError(db.provider_name)
