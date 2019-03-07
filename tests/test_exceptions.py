import unittest as unittest
from shellypython.exception import (ShellyEmptyResponse)


class TestHelpers(unittest.TestCase):

    def test_ShellyEmptyResponse1(self):
        with self.assertRaises(ShellyEmptyResponse):
            raise ShellyEmptyResponse('test')

if __name__ == '__main__':
    unittest.main()
