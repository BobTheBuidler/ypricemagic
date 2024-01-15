
from typing import Any, Iterable
from pony.orm import ProgrammingError

from y import ENVIRONMENT_VARIABLES as ENVS
from y._db import entities
from y._db.decorators import a_sync_write_db_session

def execute(sql: str) -> None:
    try:
        entities.db.execute(sql)
    except ProgrammingError as e:
        raise ValueError(e, sql) from e

def stringify_column_value(value: Any) -> str:
    if value is None:
        return 'null'
    elif isinstance(value, bytes):
        if ENVS.DB_PROVIDER == 'postgres':
            #return f"E'\\x{value.hex()}"
            return f"'{value.decode()}'::bytea"
        elif ENVS.DB_PROVIDER == 'sqlite':
            return f"X'{value.hex()}'"
        raise NotImplementedError(ENVS.DB_PROVIDER)
    elif isinstance(value, str):
        return f"'{value}'"
    elif isinstance(value, int):
        return str(value)
    else:
        raise NotImplementedError(type(value), value)
        
def build_row(row: Iterable[Any]) -> str:
    return f"({','.join(stringify_column_value(col) for col in row)})"

@a_sync_write_db_session
def insert(entity_type: entities.db.Entity, columns: Iterable[str], items: Iterable[Iterable[Any]]):
    data = ",".join(build_row(i) for i in items)
    if ENVS.DB_PROVIDER == 'sqlite':
        execute(f'insert or ignore into {entity_type.__name__.lower()} ({",".join(columns)}) values {data}')
    elif ENVS.DB_PROVIDER == 'postgres':
        execute(f'insert into {entity_type.__name__.lower()} ({",".join(columns)}) values {data} on conflict do nothing')
    else:
        raise NotImplementedError(ENVS.DB_PROVIDER)
