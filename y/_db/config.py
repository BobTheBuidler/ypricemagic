
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
        'provider': str(ENVS.DB_PROVIDER),
        'filename': f"{path.expanduser( '~' )}/.ypricemagic/ypricemagic.sqlite",
        'create_db': True,
    }
else:
    connection_settings = {
        'provider': str(ENVS.DB_PROVIDER),
        'host': str(ENVS.DB_HOST),
        'user': str(ENVS.DB_USER),
        'password': str(ENVS.DB_PASSWORD),
        'database': str(ENVS.DB_DATABASE),
    }
    if ENVS.DB_PORT:
        connection_settings['port'] = int(ENVS.DB_PORT)
