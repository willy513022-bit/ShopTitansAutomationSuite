import unittest

from core.player_profile import PlayerProfile


class TestPlayerProfile(unittest.TestCase):
    def test_default_collector_profile(self):
        profile = PlayerProfile()
        self.assertEqual(profile.mode, "COLLECTOR")
        self.assertTrue(profile.collection["keep_legendary_forever"])
        self.assertEqual(profile.pet["food_quality"], "NORMAL")
        self.assertFalse(profile.king["auto_sell"])
