import unittest

from core import DecisionContext
from evaluators import InventoryEvaluator


class InventoryEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.context = DecisionContext(world_state={})
        self.evaluator = InventoryEvaluator()

    def test_scores_inventory_gap(self):
        result = self.evaluator.evaluate(
            self.context,
            {"item": "Wood Axe", "current_stock": 4, "target_stock": 20},
        )
        self.assertTrue(result.eligible)
        self.assertEqual(32.0, result.score)
        self.assertEqual(16, result.details["missing"])

    def test_target_already_met_is_ineligible(self):
        result = self.evaluator.evaluate(
            self.context,
            {"item": "Squire Sword", "current_stock": 20, "target_stock": 20},
        )
        self.assertFalse(result.eligible)
        self.assertEqual(0.0, result.score)

    def test_unknown_inventory_is_ineligible(self):
        result = self.evaluator.evaluate(self.context, {"item": "Wood Axe"})
        self.assertFalse(result.eligible)
        self.assertIn("PROD_INVENTORY_UNKNOWN", result.rule_ids)


if __name__ == "__main__":
    unittest.main()
