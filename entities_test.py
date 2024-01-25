import unittest

from entities import Entities


class TestEntities(unittest.TestCase):
    def setUp(self):
        self.a = Entities()
        self.a.add("ent1")
        self.a.add("ent2")

    def test_get_entity(self):
        a = Entities()
        a.add("ent1")
        e = a.get("ent1")
        self.assertEqual(e["entity"], "ent1")
        self.assertNotEqual(e["entity"], "ent2", "Should not match")

        with self.assertRaises(KeyError):
            e = a.get("ent1xxx")

    def test_get_entity2(self):
        e = self.a.get("ent1")
        self.assertEqual(e["entity"], "ent1")
        self.assertNotEqual(e["entity"], "ent2", "Should not match")
        e = self.a.get("ent2")
        self.assertEqual(e["entity"], "ent2")

    def test_set_status(self):
        e = self.a.get("ent1")
        self.assertEqual(e["status"], None)

        self.a.set_status("ent1", "online")
        e = self.a.get("ent1")
        self.assertEqual(e["entity"], "ent1")
        self.assertEqual(e["status"], "online")

        with self.assertRaises(KeyError):
            e = self.a.get("ent1xxx")

    def test_iter(self):
        i = 0
        for e in self.a:
            i += 1
            e = self.a.get(e)
            if i == 1:
                self.assertEqual(e["entity"], "ent1")
                self.assertEqual(e["status"], None)
            if i == 2:
                self.assertEqual(e["entity"], "ent2")
                self.assertEqual(e["status"], None)

        self.a.set_status("ent1", "online")

        for e in self.a:
            i += 1
            e = self.a.get(e)
            if i == 1:
                self.assertEqual(e["entity"], "ent1")
                self.assertEqual(e["status"], "online")
            if i == 2:
                self.assertEqual(e["entity"], "ent2")
                self.assertEqual(e["status"], None)

    def test_filter_offline(self):
        self.a.set_status("ent1", "online")
        self.a.set_status("ent2", "offline")

        xx = list(filter(self.a.is_offline, self.a.entities))
        self.assertEqual(len(xx), 1)
        self.assertEqual(xx[0], "ent2")

    def test_len(self):
        self.assertEqual(len(self.a), 2)

    def test_set_reconfigure_single(self):
        self.a.set_status("ent1", "online")
        self.a.set_status("ent2", "offline", reconfigure=False)

        xx = list(filter(self.a.is_reconfigure, self.a.entities))
        self.assertEqual(len(xx), 1)
        self.assertEqual(xx[0], "ent1")

    def test_set_reconfigure_list_list(self):
        self.a.set_status("ent1", "online")
        self.a.set_status("ent2", "offline")
        self.a.add("ent3")
        self.a.add("ent4")

        dont_list = ["ent2", "ent3", "ent4"]
        self.a.set_dont_reconfigure(dont_list)
        xx = list(filter(self.a.is_reconfigure, self.a.entities))
        self.assertEqual(len(xx), 1)
        self.assertEqual(xx[0], "ent1")

        dont_list = ["ent2", "ent3xxx", "ent4"]
        with self.assertRaises(KeyError):
            self.a.set_dont_reconfigure(dont_list)

    def test_set_reconfigure_list_single(self):
        self.a.set_status("ent1", "online")
        self.a.set_status("ent2", "offline")

        self.a.set_dont_reconfigure("ent2")
        xx = list(filter(self.a.is_reconfigure, self.a.entities))
        self.assertEqual(len(xx), 1)
        self.assertEqual(xx[0], "ent1")

    def test_set_reconfigure_key_error(self):
        with self.assertRaises(KeyError):
            self.a.set_dont_reconfigure("ent2xxx")

    def test_nested_filters(self):
        self.a.add("ent3")
        self.a.add("ent4")

        self.a.set_status("ent1", "online")
        self.a.set_status("ent2", "offline")
        self.a.set_status("ent3", "offline", reconfigure=False)
        self.a.set_status("ent4", "offline")

        xx = self.a.get_reconfigurables()
        self.assertEqual(len(xx), 3)

        xx = self.a.get_offline()
        self.assertEqual(len(xx), 3)

        xx = list(filter(lambda x: (self.a.is_offline(x)), list(filter(lambda x: (self.a.is_reconfigure(x)), self.a.entities))))
        self.assertEqual(len(xx), 2)

        xx = self.a.get_offline_to_reconfigure()
        self.assertEqual(len(xx), 2)


if __name__ == '__main__':
    unittest.main()
