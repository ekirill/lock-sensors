from contextlib import contextmanager
from itertools import count

from psycopg2 import sql


_savepoint_count = count(0)


def begin(cursor) -> str:
    savepoint_name = str(next(_savepoint_count))
    cursor.execute(sql.SQL('SAVEPOINT {}').format(sql.Identifier(savepoint_name)))
    return savepoint_name


def commit(cursor, transaction_id: str):
    cursor.execute(sql.SQL('RELEASE SAVEPOINT {}').format(sql.Identifier(transaction_id)))


def rollback(cursor, transaction_id: str):
    cursor.execute(sql.SQL('ROLLBACK TO SAVEPOINT {}').format(sql.Identifier(transaction_id)))


class Atomic:
    def __init__(self, cursor):
        self._cursor = cursor

    def __enter__(self):
        self._transacton_id = begin(self._cursor)

    def __exit__(self, exc_type, exc_val, traceback):
        if exc_type:
            rollback(self._cursor, self._transacton_id)
            return False

        commit(self._cursor, self._transacton_id)


atomic = Atomic
