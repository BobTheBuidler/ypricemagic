
import click

from y import ENVIRONMENT_VARIABLES as ENVS
from y._db import SQLITE_PATH, delete_sqlite
from y._db.config import connection_settings

class CacheNotPopulatedError(Exception):
    pass


class yDBError(Exception):
    provider = ENVS.DB_PROVIDER
    location = SQLITE_PATH if provider == "sqlite" else connection_settings

class NewDatabaseSchemaError(yDBError):
    msg = f"\n\nA more performant ydb schema has been pooshed to prod, you must delete your ypricemagic database at {yDBError.location}"
    def __init__(self) -> None:
        if self.provider == "sqlite" and self._user_approves_sqlite_deletion():
            delete_sqlite()
        super().__init__(self.msg)

    def _user_approves_sqlite_deletion(self) -> bool:
        return click.prompt(
            self.msg + "\n\nWould you like to delete your db now?", 
            default="no", 
            type=click.Choice(["yes", "no"], case_sensitive=False), 
            confirmation_prompt=True, 
            show_default=False,
        ) == "yes"

class EEEError(ValueError):
    """raised when trying to do stuff with the eee address in the token db"""