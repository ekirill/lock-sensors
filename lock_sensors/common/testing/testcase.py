import unittest
from lock_sensors.common.settings import CONFIG


class BaseTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        if not CONFIG.get("TEST"):
            raise EnvironmentError('You must run tests with `LOCK_SENSORS_TESTING` environment variable')
        super().__init__(*args, **kwargs)
