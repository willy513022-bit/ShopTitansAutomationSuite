import unittest
from datetime import datetime, timezone

from core import PlannerDecision, ScoredDecision
from planners import DecisionTrace


class DecisionTraceTests(unittest.TestCase):
    def test_builds_trace_from_scored_decision(self):
        decision = PlannerDecision(
            planner="craft",
            action="CRAFT",
            base_priority=75,
            reason="restock",
            payload={"score_factors": ({"id": "PROD_RESTOCK", "value": 20},)},
            rule_ids=("PROD_RESTOCK",),
        )
        scored = ScoredDecision(decision, 82, {"runtime": 7})
        now = datetime(2026, 7, 19, tzinfo=timezone.utc)
        trace = DecisionTrace.from_scored_decision(scored, created_at=now)
        self.assertEqual(82, trace.final_score)
        self.assertEqual(2, len(trace.factors))
        self.assertEqual("2026-07-19T00:00:00+00:00", trace.to_dict()["created_at"])


if __name__ == "__main__":
    unittest.main()
