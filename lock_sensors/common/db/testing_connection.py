import glob
import logging
import os
from contextlib import contextmanager

import psycopg2
from psycopg2 import sql

from lock_sensors.common.db import client


logger = logging.getLogger("testing")


class TestingPool:
    def __init__(self, conf: dict):
        self._connection = psycopg2.connect(
            user=conf['USER'],
            password=conf['PASSWORD'],
            host=conf['HOST'],
            port=conf['PORT'],
            database=conf['DATABASE'],
        )

    def closeall(self):
        return self._connection.close()

    def getconn(self):
        return self._connection


@contextmanager
def testing_pool(testing_conf: dict):
    create_database(testing_conf)
    client.close_pool()
    pool = TestingPool(testing_conf)
    client._pool = pool

    create_schema()

    yield

    client.close_pool()


def create_database(testing_conf: dict):
    logger.debug(f"CREATING TEST DATABASE `{testing_conf['DATABASE']}`")
    conn = client.get_connection()

    # database operations can not be run in transaction
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(testing_conf['DATABASE'])))
    cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(testing_conf['DATABASE'])))
    conn.autocommit = False


def create_schema():
    conn = client.get_connection()
    try:
        schema_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "schema")
        cursor = conn.cursor()

        for sql_file in glob.glob(os.path.join(schema_folder, "*.sql")):
            logger.debug(f"RUNNING SQL FROM `{sql_file}`")
            with open(sql_file, 'r', encoding='utf-8') as f:
                cursor.execute(f.read())
        conn.commit()
    except:
        conn.rollback()
        raise
