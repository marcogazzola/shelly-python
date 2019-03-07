import unittest as unittest
from shellypython.shelly import (Shelly, BaseShellyAttribute, System, Roller, Relay)
import responses
import json
import logging

logging.basicConfig(level=logging.DEBUG)


class TestShelly(unittest.TestCase):
    """ test class with ko shelly"""

    def setUp(self):
        """load test data"""
        self.shelly_obj = Shelly("fakeip")

    def test_class_type(self):
        self.assertIsInstance(self.shelly_obj, Shelly)

    def test_status_class_type(self):
        self.assertIsInstance(self.shelly_obj.update_data(), Shelly)

    def test_attribute_value(self):
        self.assertIsNotNone(self.shelly_obj.update_data().main_status)

    @responses.activate
    def test_set_status_api(self):
        self.URL = 'http://fakeip/status'
        responses.add(
            responses.GET, self.URL,
            body="fakeresult",
            status=200,
            content_type='application/json'
        )

        self.assertIsInstance(self.shelly_obj.update_data(), Shelly)

    @responses.activate
    def test_set_base_info_api(self):
        self.URL = 'http://fakeip/settings'
        responses.add(
            responses.GET, self.URL,
            body="fakeresult",
            status=200,
            content_type='application/json'
        )

        self.assertIsInstance(self.shelly_obj.update_data(), Shelly)

    def test_BaseShellyAttribute(self):
        self.testobj = {'field1': 'val1', 'field2': 'val2'}
        x = BaseShellyAttribute(json.dumps(self.testobj))
        self.assertEqual(x.__dict__, self.testobj)

    def test_BaseShellyAttribute2(self):
        self.testobj = {'field1': 'val1', 'field2': 'val2'}
        x = BaseShellyAttribute(None)
        self.assertEqual(x.__dict__, {})

    def test_BaseShellyAttribute3(self):
        self.testobj = {'field1': 'val1', 'field2': 'val2'}
        x = System(None)
        self.assertIsInstance(x, System)

    def test_BaseShellyAttribute4(self):
        x = BaseShellyAttribute(None)
        self.assertIsInstance(x.as_dict(), dict)

    def test_Roller1(self):
        x = Roller(None)
        self.assertIsInstance(x, Roller)
        self.assertIsInstance(x.as_dict(), dict)

    def test_Roller2(self):
        obj = {'state': 'stop', 'current_pos': 95,
               'calibrating': False, 'positioning': True, 'status': 95}
        x = Roller(json.dumps(obj))
        self.assertIsInstance(x, Roller)
        self.assertIsInstance(x.as_dict(), dict)

    def test_Relay1(self):
        x = Relay(None)
        self.assertIsInstance(x, Relay)
        self.assertIsInstance(x.as_dict(), dict)

    def test_Relay2(self):
        obj = {'ison': False}
        x = Relay(json.dumps(obj))
        self.assertIsInstance(x, Relay)
        self.assertIsInstance(x.as_dict(), dict)


if __name__ == '__main__':
    unittest.main()
