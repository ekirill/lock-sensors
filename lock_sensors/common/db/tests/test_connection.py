from lock_sensors.common import db
from lock_sensors.common.db import transaction
from lock_sensors.common.testing.testcase import BaseTestCase


class TestDB(BaseTestCase):
    def test_connection_is_test(self):
        conn = db.get_connection()
        self.assertIn("dbname=test", conn.dsn)

    def test_transaction(self):
        cursor = db.get_connection().cursor()

        try:
            with transaction.atomic(cursor):
                cursor.execute(
                    "INSERT INTO clients (client_id, name, notification_url) VALUES (%s, %s, %s)",
                    (101, "test name 1", "test_url")
                )
                cursor.execute(
                    "INSERT INTO clients (client_id, name, notification_url) VALUES (%s, %s, %s)",
                    (102, "test name 2", "test_url ")
                )

                cursor.execute("SELECT COUNT(*) FROM clients")
                cnt = cursor.fetchone()[0]
                self.assertEqual(cnt, 4)
                raise RuntimeError('fake error')
        except RuntimeError:
            pass

        cursor.execute("SELECT COUNT(*) FROM clients")
        cnt = cursor.fetchone()[0]
        self.assertEqual(cnt, 2)

    def test_isolation_part_1(self):
        cursor = db.get_connection().cursor()
        with transaction.atomic(cursor):
            cursor.execute(
                "INSERT INTO clients (client_id, name, notification_url) VALUES (%s, %s, %s)",
                (101, "test name 1", "test_url")
            )

        cursor.execute("SELECT COUNT(*) FROM clients")
        cnt = cursor.fetchone()[0]
        self.assertEqual(cnt, 3)

    def test_isolation_part_2(self):
        cursor = db.get_connection().cursor()
        cursor.execute("SELECT COUNT(*) FROM clients")
        cnt = cursor.fetchone()[0]
        self.assertEqual(cnt, 2)
