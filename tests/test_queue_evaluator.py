import unittest

from core import DecisionContext
from evaluators import QueueEvaluator


class QueueEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.evaluator = QueueEvaluator()

    def test_scores_free_slots(self):
        context = DecisionContext(world_state={"production": {"free_slots": 3}})
        result = self.evaluator.evaluate(context, {})
        self.assertTrue(result.eligible)
        self.assertEqual(15.0, result.score)

    def test_full_queue_is_ineligible(self):
        context = DecisionContext(world_state={"production": {"free_slots": 0}})
        result = self.evaluator.evaluate(context, {})
        self.assertFalse(result.eligible)
        self.assertEqual(0.0, result.score)

    def test_metadata_overrides_world_state(self):
        context = DecisionContext(
            world_state={"production": {"free_slots": 0}},
            metadata={"production": {"free_slots": 2}},
        )
        result = self.evaluator.evaluate(context, {})
        self.assertTrue(result.eligible)
        self.assertEqual(10.0, result.score)


if __name__ == "__main__":
    unittest.main()
