import unittest

from hamqtt import HaMqtt


class TestEntities(unittest.TestCase):
    def setUp(self):
        self.a = HaMqtt()

    def test_init(self):
        self.a.init("paho")
        self.assertEqual(self.a.environment, "paho")

    def test_init_negative(self):
        with self.assertRaises(ValueError):
            self.a.init("ShouldNotWork")


if __name__ == '__main__':
    unittest.main()
