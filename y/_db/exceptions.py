import click

from y import ENVIRONMENT_VARIABLES as ENVS
from y._db import SQLITE_PATH, delete_sqlite
from y._db.config import connection_settings


class CacheNotPopulatedError(Exception):
    """Raised when the cache is not populated with the required data.

    This exception is used to indicate that an operation requiring cached data
    cannot proceed because the cache is empty or incomplete.

    Example:
        >>> raise CacheNotPopulatedError("Cache is empty, cannot proceed.")
    """

    pass


class yDBError(Exception):
    """Base class for exceptions related to the ypricemagic database.

    This class provides a foundation for database-related errors, including
    information about the database provider and location.

    Attributes:
        provider: The database provider, as specified in environment variables.
        location: The location of the database, determined by the provider type.

    Example:
        >>> raise yDBError("An error occurred with the ypricemagic database.")
    """

    provider = ENVS.DB_PROVIDER
    location = SQLITE_PATH if provider == "sqlite" else connection_settings


class NewDatabaseSchemaError(yDBError):
    """Raised when a new database schema requires the deletion of the existing database.

    This exception is triggered when a more performant ydb schema is pushed to production,
    necessitating the deletion of the current ypricemagic database.

    Example:
        >>> try:
        ...     raise NewDatabaseSchemaError()
        ... except NewDatabaseSchemaError as e:
        ...     print(e)

    See Also:
        - :class:`yDBError` for the base class of database-related exceptions.
    """

    msg = f"\n\nA more performant ydb schema has been pushed to prod, you must delete your ypricemagic database at {yDBError.location}"

    def __init__(self) -> None:
        """Initialize the NewDatabaseSchemaError.

        If the database provider is SQLite and the user approves deletion,
        the existing SQLite database will be deleted.

        Example:
            >>> error = NewDatabaseSchemaError()
            >>> print(error.msg)
        """
        if self.provider == "sqlite" and self._user_approves_sqlite_deletion():
            delete_sqlite()
        super().__init__(self.msg)

    def _user_approves_sqlite_deletion(self) -> bool:
        """Prompt the user for approval to delete the SQLite database.

        Returns:
            bool: True if the user approves the deletion, False otherwise.

        Example:
            >>> error = NewDatabaseSchemaError()
            >>> error._user_approves_sqlite_deletion()
            Would you like to delete your db now? [no]: yes
            True
        """
        return (
            click.prompt(
                self.msg + "\n\nWould you like to delete your db now?",
                default="no",
                type=click.Choice(("yes", "no"), case_sensitive=False),
                confirmation_prompt=True,
                show_default=False,
            )
            == "yes"
        )


class EEEError(ValueError):
    """Raised when attempting to perform operations with the EEE address in the token database.

    This exception indicates that an invalid operation involving the EEE address
    was attempted in the context of the token database.

    Example:
        >>> raise EEEError("Invalid operation with the EEE address.")
    """

    pass
