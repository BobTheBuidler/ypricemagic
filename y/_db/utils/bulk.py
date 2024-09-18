
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Iterable
from pony.orm import Database, DatabaseError, commit

from y._db import entities
from y._db.decorators import a_sync_write_db_session, retry_locked


logger = logging.getLogger(__name__)

class SQLError(ValueError):
    """
    Custom exception for SQL-related errors.
    
    This exception wraps an Exception raised when executing a SQL statement.
    It includes both the original error and the SQL statement that caused it.
    """

@retry_locked
def execute(sql: str, *, db: Database = entities.db) -> None:
    """
    Execute a SQL statement with retry logic for locked databases.

    This function attempts to execute the given SQL statement and commit the changes.
    If the database is locked, the operation will be retried based on the @:class:`retry_locked` decorator.
    
    Args:
        sql: The SQL statement to execute.
        db: The database to execute the statement on. Defaults to entities.db.

    Raises:
        SQLError: If there's an error executing the SQL statement, except for "database is locked" errors.

    Note:
        - The function logs the SQL statement at debug level before execution.
        - If a "database is locked" error occurs, it's re-raised to trigger the retry mechanism.
        - For all other DatabaseErrors, it logs a warning and raises a SQLError with the original error and SQL statement.
    """
    try:
        logger.debug("EXECUTING SQL")
        logger.debug(sql)
        db.execute(sql)
        commit()
    except DatabaseError as e:
        if str(e) == "database is locked":
            raise
        logger.warning("%s %s when executing SQL`%s`", e.__class__.__name__, e, sql)
        raise SQLError(e, sql) from e

def stringify_column_value(value: Any, provider: str) -> str:
    """
    Convert a Python value to a string representation suitable for SQL insertion.

    This function handles various Python types and converts them to SQL-compatible string representations.
    It supports different database providers (currently 'postgres' and 'sqlite') for certain data types.

    Args:
        value: The value to stringify. Can be None, bytes, str, int, Decimal, or datetime.
        provider: The database provider. Currently supports 'postgres' and 'sqlite'.

    Returns:
        A string representation of the value suitable for SQL insertion.

    Raises:
        NotImplementedError: If the value type is not supported or if an unsupported provider is specified for bytes.

    Note:
        - None values are converted to 'null'.
        - Bytes are handled differently for 'postgres' (converted to bytea) and 'sqlite' (converted to hex).
        - Strings are wrapped in single quotes.
        - Integers and Decimals are converted to their string representation.
        - Datetimes are converted to UTC and formatted as ISO8601 strings.
    """
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
    """
    Build a SQL row string from an iterable of values.

    This function takes an iterable of values and converts each value to its SQL string representation,
    then combines them into a single row string suitable for SQL insertion.

    Args:
        row: An iterable of values to be converted into a SQL row string.
        provider: The database provider to use for value conversion.

    Returns:
        A string representing a SQL row, formatted as (value1,value2,...).

    Note:
        This function uses :func:`stringify_column_value` internally to convert each value.
    """
    return f"({','.join(stringify_column_value(col, provider) for col in row)})"

@a_sync_write_db_session
def insert(
    entity_type: entities.db.Entity, 
    columns: Iterable[str], 
    items: Iterable[Iterable[Any]],
    *,
    db: Database = entities.db,
) -> None:
    """
    Perform a bulk insert operation into the database.

    This function constructs and executes an INSERT statement for multiple rows of data.
    It supports different syntax for SQLite and PostgreSQL databases.

    Args:
        entity_type: The database entity type to insert into.
        columns: An iterable of column names.
        items: An iterable of iterables, where each inner iterable represents a row of data to insert.
        db: The database to perform the insertion on. Defaults to entities.db.

    Raises:
        NotImplementedError: If an unsupported database provider is used.

    Note:
        - For SQLite, it uses 'INSERT OR IGNORE' syntax.
        - For PostgreSQL, it uses 'INSERT ... ON CONFLICT DO NOTHING' syntax.
    """
    entity_name = entity_type.__name__.lower()
    data = ",".join(build_row(i, db.provider_name) for i in items)
    if db.provider_name == 'sqlite':
        execute(f'insert or ignore into {entity_name} ({",".join(columns)}) values {data}', db=db)
    elif db.provider_name == 'postgres':
        execute(f'insert into {entity_name} ({",".join(columns)}) values {data} on conflict do nothing', db=db)
    else:
        raise NotImplementedError(db.provider_name)
    logger.debug('inserted %s %ss to ydb', len(items), entity_name)
