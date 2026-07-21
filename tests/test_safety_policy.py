import unittest

from core.player_profile import PlayerProfile, SafetyPolicy


class TestSafetyPolicy(unittest.TestCase):
    def test_default_safety(self):
        policy = SafetyPolicy(PlayerProfile())
        self.assertFalse(policy.may_use_gems("upgrade"))
        self.assertFalse(policy.may_use_gems("repair"))
        self.assertEqual(policy.repair_currency(), "GOLD")
        self.assertFalse(policy.may_auto_sell_to_king())
