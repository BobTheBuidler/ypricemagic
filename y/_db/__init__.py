
import os

from pony.orm import Database, BindingError, DatabaseError, TransactionError

from y._db.config import SQLITE_PATH


def bind_db(db: Database, **connection_settings) -> None:
    try:
        db.bind(**connection_settings)
    except BindingError as e:
        if not str(e).startswith('Database object was already bound to'):
            raise

def generate_mapping(db: Database) -> None:
    try:
        db.generate_mapping(create_tables=True)
    except BindingError as e:
        if str(e) != "Mapping was already generated":
            raise
    except DatabaseError as e:
        if "no such column: " in str(e) or ("column" in str(e) and " does not exist" in str(e)):
            from y._db.exceptions import NewDatabaseSchemaError
            raise NewDatabaseSchemaError from e
    except TransactionError as e:
        if str(e) != "@db_session-decorated create_tables() function with `ddl` option cannot be called inside of another db_session":
            raise
    
def delete_sqlite() -> None:
    os.remove(SQLITE_PATH)
