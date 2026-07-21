import unittest

from core.account_capabilities import AccountCapabilities


class TestAccountCapabilities(unittest.TestCase):
    def test_defaults_and_update(self):
        caps = AccountCapabilities()
        self.assertEqual(caps.production_queue_capacity, 10)
        self.assertEqual(caps.expedition_team_capacity, 8)

        caps.update_from_observation(production_queue_capacity=11)
        self.assertEqual(caps.production_queue_capacity, 11)

    def test_negative_capacity_rejected(self):
        caps = AccountCapabilities(production_queue_capacity=-1)
        with self.assertRaises(ValueError):
            caps.validate()
