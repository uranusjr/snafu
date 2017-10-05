import unittest.mock
import sys


def pytest_collectstart():
    sys.modules['winreg'] = unittest.mock.Mock()
