import errno
from os import mkdir, path

from y import ENVIRONMENT_VARIABLES as ENVS

SQLITE_DIR = f"{path.expanduser( '~' )}/.ypricemagic"
SQLITE_PATH = f"{SQLITE_DIR}/ypricemagic.sqlite"

if ENVS.DB_PROVIDER == "sqlite":
    try:
        mkdir(SQLITE_DIR)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    connection_settings = {
        "provider": str(ENVS.DB_PROVIDER),
        "filename": SQLITE_PATH,
        "create_db": True,
    }
else:
    connection_settings = {
        "provider": str(ENVS.DB_PROVIDER),
        "host": str(ENVS.DB_HOST),
        "user": str(ENVS.DB_USER),
        "password": str(ENVS.DB_PASSWORD),
        "database": str(ENVS.DB_DATABASE),
    }
    if ENVS.DB_PORT:
        connection_settings["port"] = int(ENVS.DB_PORT)

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
