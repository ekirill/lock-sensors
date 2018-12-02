#!/usr/bin/env python

import logging
import unittest

from lock_sensors.common.settings import CONFIG
from lock_sensors.common.testing.runner import TransactionRunner

if CONFIG.get('DEBUG'):
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)


def main():
    unittest.main(module=None, testRunner=TransactionRunner)


main()
