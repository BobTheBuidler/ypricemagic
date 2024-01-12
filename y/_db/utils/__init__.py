
from y._db import bind_db, generate_mapping
from y._db.config import connection_settings
from y._db.entities import db
from y._db.utils.utils import ensure_chain, get_chain, get_block

bind_db(db, **connection_settings)
generate_mapping(db)

__all__ = 'get_chain', 'get_block'