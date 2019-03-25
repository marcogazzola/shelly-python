import unittest as unittest
from shellypython.shelly import (Shelly, Cloud, System, Wifi_sta, Firmware, Mqtt)
from shellypython.helpers import (Call_shelly_api, Get_item_safe, Rssi_to_percentage)
from shellypython.exception import (ShellyNetworkException, ShellyUnreachableException,
    ShellyAccessForbitten)
import responses


class TestHelpers(unittest.TestCase):

    def setUp(self):
        self.list = ['test1', 'test2', 'test3']
        self.dict = {'test1': 'Test n° 1', 'test2': 'Test n° 2', 'test3': 'Test n° 3'}
        self.keyOk = 'test1'
        self.valueOk = 'Test n° 1'
        self.keyKo = 'bad value'
        self.default = 'defaultValue'

    def test_item_safe_empty(self):
        self.assertEqual(Get_item_safe([], self.keyKo, self.default), self.default)

    def test_item_safe_generic_error(self):
        self.assertEqual(Get_item_safe(None, self.keyKo, self.default), self.default)

    def test_list_item_safe_index_error(self):
        self.assertEqual(Get_item_safe(self.list, self.keyKo, self.default), self.default)

    def test_list_item_safe_ok(self):
        self.assertEqual(Get_item_safe(self.list, self.keyOk, self.default), self.keyOk)

    def test_dict_item_safe_index_error(self):
        self.assertEqual(Get_item_safe(self.dict, self.keyKo, self.default), self.default)

    def test_dict_item_safe_ok(self):
        self.assertEqual(Get_item_safe(self.dict, self.keyOk, self.default), self.valueOk)

    def test_call_shelly_api_ko_net_ex(self):
        with self.assertRaises(ShellyNetworkException):
            Call_shelly_api('192.168.1.1')

    @responses.activate
    def test_call_shelly_api_ko_unreach(self):
        self.URL = 'http://fakeapi/status'
        responses.add(
            responses.GET, self.URL,
            body="fakeresult",
            status=401,
            content_type='application/json'
        )
        with self.assertRaises(ShellyAccessForbitten):
            Call_shelly_api('http://fakeapi/status')

    @responses.activate
    def test_call_shelly_api_auth_ko(self):
        self.URL = 'http://fakeapi/status'
        responses.add(
            responses.GET, self.URL,
            body="fakeresult",
            status=401,
            content_type='application/json'
        )
        with self.assertRaises(ShellyAccessForbitten):
            Call_shelly_api('http://fakeapi/status', 'user', 'password')

    @responses.activate
    def test_call_shelly_api_auth_ok(self):
        self.URL = 'http://fakeapi/status'
        responses.add(
            responses.GET, self.URL,
            body="fakeresult",
            status=200,
            content_type='application/json'
        )
        ret_val = Call_shelly_api('http://fakeapi/status', 'user', 'password')
        self.assertIsInstance(ret_val, str)

    @responses.activate
    def test_call_shelly_api_ok(self):
        self.URL = 'http://fakeapi/status'
        responses.add(
            responses.GET, self.URL,
            body=open('tests/fixtures/status_ok.json').read(),
            status=200,
            content_type='application/json'
            )
        ret_val = Call_shelly_api('http://fakeapi/status')
        self.assertIsInstance(ret_val, str)

    @responses.activate
    def test_call_shelly_api_response_ok(self):
        self.URL = 'http://fakeapi/status'
        responses.add(
            responses.GET, self.URL,
            body=open('tests/fixtures/status_ok.json').read(),
            status=200,
            content_type='application/json'
            )

        self.URL = 'http://fakeapi/shelly'
        responses.add(
            responses.GET, self.URL,
            body=open('tests/fixtures/shelly_ok.json').read(),
            status=200,
            content_type='application/json'
            )

        self.shelly = Shelly('fakeapi').update_data()

        self.assertIsInstance(self.shelly, Shelly)
        self.assertIsNotNone(self.shelly.system)
        self.assertIsInstance(self.shelly.wifi_sta, Wifi_sta)
        self.assertIsInstance(self.shelly.cloud, Cloud)
        self.assertIsInstance(self.shelly.system, System)
        self.assertIsInstance(self.shelly.firmware, Firmware)
        self.assertIsInstance(self.shelly.mqtt, Mqtt)

        self.assertEqual(self.shelly.wifi_sta.ssid, 'mySuperSecretNetwork')

    @responses.activate
    def test_call_shelly_api_response_ko(self):
        self.URL = 'http://fakeapi/status'
        responses.add(
            responses.GET, self.URL,
            body=None,
            status=400,
            content_type='application/json'
            )

        self.URL = 'http://fakeapi/shelly'
        responses.add(
            responses.GET, self.URL,
            body=None,
            status=500,
            content_type='application/json'
            )

        self.shelly = Shelly('fakeapi').update_data()

        self.assertIsInstance(self.shelly, Shelly)
        self.assertIsNotNone(self.shelly.system)
        self.assertIsInstance(self.shelly.wifi_sta, Wifi_sta)
        self.assertIsInstance(self.shelly.cloud, Cloud)
        self.assertIsInstance(self.shelly.system, System)
        self.assertIsInstance(self.shelly.firmware, Firmware)
        self.assertIsInstance(self.shelly.mqtt, Mqtt)
        self.assertIsNone(self.shelly.wifi_sta.ssid)

    def test_Rssi_to_percentage(self):
        self.assertTrue(Rssi_to_percentage(-50) <= 100)
        self.assertTrue(Rssi_to_percentage(-50) >= 0)
        self.assertTrue(Rssi_to_percentage(-10) >= 0)

if __name__ == '__main__':
    unittest.main()
