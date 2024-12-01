import os

from pony.orm import Database, BindingError, DatabaseError, TransactionError

from y._db.config import SQLITE_PATH


def bind_db(db: Database, **connection_settings) -> None:
    """Bind a database to the given connection settings.

    This function attempts to bind a `pony.orm.Database` instance to the specified
    connection settings. If the database is already bound, it will not raise an error.

    Args:
        db (Database): The database instance to bind.
        **connection_settings: Arbitrary keyword arguments representing the connection settings.

    Raises:
        BindingError: If the database object was already bound to different settings.

    Example:
        >>> from pony.orm import Database
        >>> db = Database()
        >>> bind_db(db, provider='sqlite', filename=':memory:')
    """
    try:
        db.bind(**connection_settings)
    except BindingError as e:
        if not str(e).startswith("Database object was already bound to"):
            raise


def generate_mapping(db: Database) -> None:
    """Generate the mapping for the database entities.

    This function generates the mapping for the entities in the database and creates
    the tables if they do not exist. It handles specific exceptions related to binding
    and database errors.

    Args:
        db (Database): The database instance for which to generate the mapping.

    Raises:
        BindingError: If the mapping was already generated.
        DatabaseError: If there is an issue with the database schema, such as a missing column.
        TransactionError: If the function is called inside another db_session.

    Example:
        >>> from pony.orm import Database
        >>> db = Database()
        >>> generate_mapping(db)
    """
    try:
        db.generate_mapping(create_tables=True)
    except BindingError as e:
        if str(e) != "Mapping was already generated":
            raise
    except DatabaseError as e:
        if "no such column: " in str(e) or (
            "column" in str(e) and " does not exist" in str(e)
        ):
            from y._db.exceptions import NewDatabaseSchemaError

            raise NewDatabaseSchemaError from e
    except TransactionError as e:
        if (
            str(e)
            != "@db_session-decorated create_tables() function with `ddl` option cannot be called inside of another db_session"
        ):
            raise


def delete_sqlite() -> None:
    """Delete the SQLite database file.

    This function removes the SQLite database file located at the path specified by
    `SQLITE_PATH`. It is useful for resetting the database state or handling schema
    changes that require a fresh database.

    Raises:
        FileNotFoundError: If the SQLite file does not exist.

    Example:
        >>> delete_sqlite()
    """
    os.remove(SQLITE_PATH)
