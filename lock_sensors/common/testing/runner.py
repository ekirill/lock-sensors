import copy
import logging
from unittest import TextTestRunner, TextTestResult

from lock_sensors.common.db import transaction
from lock_sensors.common.db.client import get_connection
from lock_sensors.common.db.testing_connection import testing_pool
from lock_sensors.common.settings import CONFIG


logger = logging.getLogger("testing")


class TransactionTestResult(TextTestResult):
    _transaction_id = None

    def startTest(self, test):
        self._transaction_id = transaction.begin(get_connection().cursor())
        super().startTest(test)

    def stopTest(self, test):
        super().stopTest(test)
        if not self._transaction_id:
            raise RuntimeError("Could not find test transaction. Something goes wrong, test Was not run in transaction")
        transaction.rollback(get_connection().cursor(), self._transaction_id)


class TransactionRunner(TextTestRunner):
    resultclass = TransactionTestResult

    def run(self, *args, **kwargs):
        testing_conf = copy.deepcopy(CONFIG['DATABASE'])
        testing_conf['DATABASE'] = f"test_{CONFIG['DATABASE']['DATABASE']}"

        with testing_pool(testing_conf):
            logger.debug("=" * 20 + " STARTING TESTS " + "=" * 20)
            try:
                result = super().run(*args, **kwargs)
                return result
            except BaseException as e:
                logger.error(e)
