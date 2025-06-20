"""
This module configures the database connection settings for ypricemagic.

The configuration is determined by the environment variables defined in the
:mod:`y.ENVIRONMENT_VARIABLES` module, which is imported as `ENVS` in this file.
Depending on the value of :attr:`ENVS.DB_PROVIDER`, the module sets up connection
settings for either SQLite or another database provider.

Examples:
    If using SQLite as the database provider, the configuration will create
    a directory and file for the SQLite database:

    >>> from y._db import config
    >>> config.connection_settings
    {'provider': 'sqlite', 'filename': '/home/user/.ypricemagic/ypricemagic.sqlite', 'create_db': True}

    If using another database provider, the configuration will include
    connection details such as host, user, and password:

    >>> from y._db import config
    >>> config.connection_settings
    {'provider': 'postgresql', 'host': 'localhost', 'user': 'user', 'password': 'password', 'database': 'ypricemagic'}

See Also:
    - :mod:`y.ENVIRONMENT_VARIABLES` for the environment variables used in the configuration.
"""

import errno
from os import mkdir, path
from typing import Final

from y import ENVIRONMENT_VARIABLES as ENVS


DEFAULT_SQLITE_DIR: Final = f"{path.expanduser( '~' )}/.ypricemagic"

db_provider: Final = str(ENVS.DB_PROVIDER)

if db_provider == "sqlite":
    if ENVS.SQLITE_PATH._using_default:
        try:
            mkdir(DEFAULT_SQLITE_DIR)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    connection_settings = {
        "provider": db_provider,
        "filename": str(ENVS.SQLITE_PATH),
        "create_db": True,
    }
else:
    connection_settings = {
        "provider": db_provider,
        "host": str(ENVS.DB_HOST),
        "user": str(ENVS.DB_USER),
        "password": str(ENVS.DB_PASSWORD),
        "database": str(ENVS.DB_DATABASE),
    }
    if ENVS.DB_PORT:
        connection_settings["port"] = int(ENVS.DB_PORT)
