import unittest

from core.player_profile import CollectionPolicy, PlayerProfile, SellDecision


class TestCollectionPolicy(unittest.TestCase):
    def setUp(self):
        self.policy = CollectionPolicy(PlayerProfile())

    def test_legendary_is_never_sold(self):
        result = self.policy.can_sell(
            item_name="Any Item",
            quality="Legendary",
            collection_complete=True,
        )
        self.assertEqual(result, SellDecision.DENY_LEGENDARY)

    def test_non_normal_is_kept_until_collection_complete(self):
        blocked = self.policy.can_sell(
            item_name="Rare Sword",
            quality="Rare",
            collection_complete=False,
        )
        allowed = self.policy.can_sell(
            item_name="Rare Sword",
            quality="Rare",
            collection_complete=True,
        )
        self.assertEqual(blocked, SellDecision.DENY_COLLECTION_INCOMPLETE)
        self.assertEqual(allowed, SellDecision.ALLOW)

    def test_normal_can_be_sold(self):
        result = self.policy.can_sell(
            item_name="Normal Sword",
            quality="Normal",
            collection_complete=False,
        )
        self.assertEqual(result, SellDecision.ALLOW)
