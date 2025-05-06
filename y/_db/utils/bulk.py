import logging
from typing import Any, Iterable, Sequence
from pony.orm import Database, DatabaseError, commit

from a_sync import a_sync

from y._db import entities
from y._db.common import make_executor
from y._db.decorators import db_session_retry_locked, retry_locked
from y._db.utils.stringify import build_query


logger = logging.getLogger(__name__)
_logger_debug = logger.debug


_bulk_executor = make_executor(1, 8, "ypricemagic db executor [bulk]")


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
    If the database is locked, the operation will be retried based on the :func:`~y._db.decorators.retry_locked` decorator.

    Args:
        sql: The SQL statement to execute.
        db: The database to execute the statement on. Defaults to :attr:`~y._db.entities.db`.

    Raises:
        SQLError: If there's an error executing the SQL statement, except for "database is locked" errors.

    Note:
        - The function logs the message "EXECUTING SQL" and the SQL statement at debug level before execution.
        - If a "database is locked" error occurs, it's re-raised to trigger the retry mechanism.
        - For all other :class:`~pony.orm.core.DatabaseError`, it logs a warning and raises a :class:`SQLError` with the original error and SQL statement.

    Examples:
        >>> execute("INSERT INTO my_table (column1, column2) VALUES ('value1', 'value2')")
        >>> execute("DELETE FROM my_table WHERE column1 = 'value1'")
    """
    try:
        _logger_debug("EXECUTING SQL")
        _logger_debug(sql)
        db.execute(sql)
        commit()
    except DatabaseError as e:
        if str(e) == "database is locked":
            raise
        logger.warning("%s %s when executing SQL`%s`", e.__class__.__name__, e, sql)
        raise SQLError(e, sql) from e


@a_sync(default="async", executor=_bulk_executor)
@db_session_retry_locked
def insert(
    entity_type: entities.db.Entity,  # type: ignore [name-defined]
    columns: Sequence[str],
    items: Sequence[Iterable[Any]],
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
        db: The database to perform the insertion on. Defaults to :attr:`~y._db.entities.db`.

    Raises:
        NotImplementedError: If an unsupported database provider is used.

    Note:
        - For SQLite, it uses 'INSERT OR IGNORE' syntax.
        - For PostgreSQL, it uses 'INSERT ... ON CONFLICT DO NOTHING' syntax.

    Examples:
        >>> insert(MyEntity, ['column1', 'column2'], [['value1', 'value2'], ['value3', 'value4']])
        >>> insert(MyEntity, ['column1', 'column2'], [['value1', 'value2']], db=my_db)

    See Also:
        - :func:`execute`
    """
    entity_name = entity_type.__name__.lower()
    sql = build_query(db.provider_name, entity_name, columns, items)
    execute(sql, db=db)
    _logger_debug("inserted %s %ss to ydb", len(items), entity_name)
