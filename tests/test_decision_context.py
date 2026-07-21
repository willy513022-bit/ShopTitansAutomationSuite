import unittest

from core import DecisionContext, Strategy


class DecisionContextTests(unittest.TestCase):
    def test_copies_mutable_inputs(self):
        modifiers = {"collection": 5}
        metadata = {"screen": "SHOP"}
        context = DecisionContext(
            world_state={"ready": 1},
            runtime_modifiers=modifiers,
            metadata=metadata,
            rule_ids=["ST-001"],
        )

        modifiers["collection"] = 99
        metadata["screen"] = "UNKNOWN"

        self.assertEqual(context.runtime_modifiers["collection"], 5.0)
        self.assertEqual(context.metadata["screen"], "SHOP")
        self.assertEqual(context.rule_ids, ("ST-001",))

    def test_select_context_uses_strategy_and_modifiers(self):
        from core import PlannerDecision, Scheduler

        context = DecisionContext(
            world_state=None,
            strategy=Strategy(),
            runtime_modifiers={"lostcity": 20},
        )
        result = Scheduler().select_context(
            [
                PlannerDecision("Collection", "DONATE", 96, "Ready"),
                PlannerDecision("LostCity", "BOSS", 80, "Ready"),
            ],
            context,
        )

        self.assertEqual(result.winner.decision.planner, "LostCity")


if __name__ == "__main__":
    unittest.main()
