from psycopg2.pool import SimpleConnectionPool

from lock_sensors.common.settings import CONFIG


_pool = None


# this pool is not thread safe!
def _init_pool(conf: dict):
    global _pool
    if _pool is None:
        _pool = SimpleConnectionPool(
            1, 3,
            user=conf['USER'],
            password=conf['PASSWORD'],
            host=conf['HOST'],
            port=conf['PORT'],
            database=conf['DATABASE'],
        )


def get_pool() -> SimpleConnectionPool:
    global _pool
    _init_pool(CONFIG["DATABASE"])
    return _pool


def close_pool():
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None


def get_connection():
    return get_pool().getconn()
