
from pony.orm import BindingError, TransactionError

from y._db.config import connection_settings
from y._db.entities import db
from y._db.utils.utils import get_chain, get_block

        
try:
    db.bind(**connection_settings)
    db.generate_mapping(create_tables=True)
except TransactionError as e:
    if str(e) != "@db_session-decorated create_tables() function with `ddl` option cannot be called inside of another db_session":
        raise e
except BindingError as e:
    if not str(e).startswith('Database object was already bound to'):
        raise e

__all__ = 'get_chain', 'get_block'