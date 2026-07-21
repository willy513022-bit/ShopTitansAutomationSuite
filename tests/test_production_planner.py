import unittest

from core import DecisionContext
from planners import ProductionPlanner


class ProductionPlannerTests(unittest.TestCase):
    def setUp(self):
        self.planner = ProductionPlanner()

    def test_returns_none_when_snapshot_is_missing(self):
        self.assertIsNone(self.planner.evaluate(DecisionContext(world_state={})))

    def test_returns_none_when_queue_is_full(self):
        context = DecisionContext(world_state={"production": {"free_slots": 0, "restock_needed": True}})
        self.assertIsNone(self.planner.evaluate(context))

    def test_returns_none_when_restock_is_not_needed(self):
        context = DecisionContext(world_state={"production": {"free_slots": 2, "restock_needed": False}})
        self.assertIsNone(self.planner.evaluate(context))

    def test_creates_safe_craft_candidate(self):
        context = DecisionContext(
            world_state={"production": {
                "free_slots": 2,
                "restock_needed": True,
                "target_item": "Squire Sword",
            }}
        )
        decision = self.planner.evaluate(context)
        self.assertIsNotNone(decision)
        self.assertEqual("craft", decision.planner)
        self.assertEqual("CRAFT", decision.action)
        self.assertEqual("Squire Sword", decision.payload["target_item"])
        self.assertEqual(("PROD_FREE_SLOT", "PROD_RESTOCK"), decision.rule_ids)

    def test_selects_largest_inventory_gap(self):
        context = DecisionContext(
            world_state={"production": {
                "free_slots": 2,
                "candidates": [
                    {"item": "Squire Sword", "current_stock": 18, "target_stock": 20},
                    {"item": "Wood Axe", "current_stock": 4, "target_stock": 20},
                ],
            }}
        )
        decision = self.planner.evaluate(context)
        self.assertIsNotNone(decision)
        self.assertEqual("Wood Axe", decision.payload["target_item"])
        self.assertIn("PROD_INVENTORY_GAP", decision.rule_ids)
        self.assertIn("PROD_QUEUE_CAPACITY", decision.rule_ids)

    def test_skips_candidates_that_already_meet_target(self):
        context = DecisionContext(
            world_state={"production": {
                "free_slots": 2,
                "candidates": [
                    {"item": "Squire Sword", "current_stock": 20, "target_stock": 20},
                ],
            }}
        )
        self.assertIsNone(self.planner.evaluate(context))


if __name__ == "__main__":
    unittest.main()
