import unittest

from core import DecisionContext, PlannerDecision, Strategy
from planners import BasePlanner, PlannerManager


class StaticPlanner(BasePlanner):
    def __init__(self, name, priority=None):
        self._name = name
        self.priority = priority

    @property
    def name(self):
        return self._name

    def evaluate(self, context):
        if self.priority is None:
            return None
        return PlannerDecision(self.name, "RUN", self.priority, "test")


class BrokenPlanner(StaticPlanner):
    def evaluate(self, context):
        raise RuntimeError("boom")


class PlannerManagerTests(unittest.TestCase):
    def setUp(self):
        self.context = DecisionContext(world_state={}, strategy=Strategy())

    def test_collects_non_empty_candidates(self):
        manager = PlannerManager([StaticPlanner("craft", 10), StaticPlanner("market")])
        decisions = manager.collect(self.context)
        self.assertEqual(1, len(decisions))
        self.assertEqual("craft", decisions[0].planner)

    def test_duplicate_registration_is_rejected(self):
        manager = PlannerManager([StaticPlanner("craft", 10)])
        with self.assertRaises(ValueError):
            manager.register(StaticPlanner("CRAFT", 20))

    def test_failure_isolated_in_non_strict_mode(self):
        manager = PlannerManager([BrokenPlanner("broken"), StaticPlanner("craft", 10)])
        result = manager.collect_detailed(self.context)
        self.assertEqual(1, len(result.decisions))
        self.assertEqual("RuntimeError", result.failures[0].error_type)

    def test_select_integrates_with_scheduler(self):
        manager = PlannerManager([StaticPlanner("craft", 10), StaticPlanner("market", 20)])
        result = manager.select(self.context)
        self.assertEqual("market", result.winner.decision.planner)


if __name__ == "__main__":
    unittest.main()
