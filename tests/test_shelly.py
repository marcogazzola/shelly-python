import unittest as unittest
from shellypython.shelly import (Shelly, Attributes)
from shellypython.const import (DEVICE_READY, DEVICE_NOT_READY)
from shellypython.pyjson import PyJSON
from shellypython.AbstractBase import AbstractBase

import logging

logging.basicConfig(level=logging.DEBUG)


class TestKoShelly(unittest.TestCase):
    """ test class with ko shelly"""

    def setUp(self):
        """load test data"""
        self.shelly_obj = Shelly("fakeip")

    def test_class_type(self):
        self.assertIsInstance(self.shelly_obj, Shelly)

    def test_status_class_type(self):
        self.assertIsInstance(self.shelly_obj.get_shelly_status(), Shelly)

    def test_attribute_value(self):
        self.assertIsNone(self.shelly_obj.get_shelly_status().shelly_attributes)


class TestOkShelly(unittest.TestCase):
    """ test class with ko shelly"""

    def setUp(self):
        """load test data"""
        self.shelly_obj = Shelly("fakeip")

    def test_class_type(self):
        self.assertIsInstance(self.shelly_obj, Shelly)

    def test_status_class_type(self):
        self.assertIsInstance(self.shelly_obj.get_shelly_status(), Shelly)

    def test_attribute_value(self):
        self.assertIsNone(self.shelly_obj.get_shelly_status().shelly_attributes)


if __name__ == '__main__':
    unittest.main()
