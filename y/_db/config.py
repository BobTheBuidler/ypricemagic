
from y import ENVIRONMENT_VARIABLES as ENVS
import errno
from os import mkdir, path

if ENVS.DB_PROVIDER == "sqlite":
    try:
        mkdir(f"{path.expanduser( '~' )}/.ypricemagic")
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    connection_settings = {
        'provider': ENVS.DB_PROVIDER,
        'filename': f"{path.expanduser( '~' )}/.ypricemagic/ypricemagic.sqlite"
    }
else:
    connection_settings = {
        'provider': ENVS.DB_PROVIDER,
        'host': ENVS.DB_HOST,
        'user': ENVS.DB_USER,
        'password': ENVS.DB_PASSWORD,
        'database': ENVS.DB_DATABASE,
    }
