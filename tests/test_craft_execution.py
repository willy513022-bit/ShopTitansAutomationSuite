import unittest

from core.planner_decision import PlannerDecision
from navigation import (
    NavigationStateTracker,
    Navigator,
    Screen,
    TransitionAction,
    build_default_screen_graph,
)
from runtime.craft_execution import (
    CraftExecutionPlanner,
    CraftExecutionStepKind,
)


class CraftExecutionPlannerTests(
    unittest.TestCase
):
    def setUp(self):
        self.tracker = NavigationStateTracker()

        self.navigator = Navigator(
            build_default_screen_graph(),
            self.tracker,
        )

        self.planner = CraftExecutionPlanner(
            self.navigator
        )

    def make_decision(
        self,
        *,
        target_item="Bleakspire Roots",
        requested_count=1,
    ):
        return PlannerDecision(
            planner="blueprint",
            action="CRAFT",
            base_priority=80.0,
            reason="Blueprint test",
            payload={
                "target_item": target_item,
                "requested_count": requested_count,
            },
        )

    def test_shop_to_craft_plan(self):
        self.tracker.update(
            Screen.SHOP,
            0.99,
        )

        plan = self.planner.plan(
            self.make_decision()
        )

        self.assertEqual(
            plan.target_item,
            "Bleakspire Roots",
        )

        self.assertEqual(
            plan.requested_count,
            1,
        )

        self.assertEqual(
            plan.navigation.screens(),
            (
                Screen.SHOP,
                Screen.CRAFT,
            ),
        )

        self.assertEqual(
            len(plan.navigation.transitions),
            1,
        )

        self.assertEqual(
            plan.navigation.transitions[0].action,
            TransitionAction.OPEN_CRAFT,
        )

        self.assertTrue(
            plan.requires_navigation
        )

    def test_navigation_steps_are_preserved(
        self,
    ):
        self.tracker.update(
            Screen.SHOP,
            0.99,
        )

        plan = self.planner.plan(
            self.make_decision()
        )

        kinds = tuple(
            step.kind
            for step in plan.steps
        )

        self.assertEqual(
            kinds,
            (
                CraftExecutionStepKind.NAVIGATE,
                CraftExecutionStepKind.FIND_ITEM,
                CraftExecutionStepKind.SELECT_ITEM,
                CraftExecutionStepKind.START_CRAFT,
                CraftExecutionStepKind.VERIFY_CRAFT_STARTED,
            ),
        )

        first = plan.steps[0]

        self.assertIsNotNone(
            first.transition
        )

        assert first.transition is not None

        self.assertEqual(
            first.transition.action,
            TransitionAction.OPEN_CRAFT,
        )

    def test_craft_steps_follow_navigation(
        self,
    ):
        self.tracker.update(
            Screen.SHOP,
            0.99,
        )

        plan = self.planner.plan(
            self.make_decision()
        )

        kinds = tuple(
            step.kind
            for step in plan.steps
        )

        self.assertEqual(
            kinds[-4:],
            (
                CraftExecutionStepKind.FIND_ITEM,
                CraftExecutionStepKind.SELECT_ITEM,
                CraftExecutionStepKind.START_CRAFT,
                CraftExecutionStepKind.VERIFY_CRAFT_STARTED,
            ),
        )

    def test_already_on_craft_screen(
        self,
    ):
        self.tracker.update(
            Screen.CRAFT,
            0.99,
        )

        plan = self.planner.plan(
            self.make_decision()
        )

        self.assertFalse(
            plan.requires_navigation
        )

        self.assertEqual(
            plan.navigation.transitions,
            (),
        )

        self.assertEqual(
            plan.steps[0].kind,
            CraftExecutionStepKind.FIND_ITEM,
        )

    def test_requested_count_defaults_to_one(
        self,
    ):
        self.tracker.update(
            Screen.CRAFT,
            0.99,
        )

        decision = PlannerDecision(
            planner="craft",
            action="CRAFT",
            base_priority=50,
            reason="test",
            payload={
                "target_item": "Squire Sword",
            },
        )

        plan = self.planner.plan(
            decision
        )

        self.assertEqual(
            plan.requested_count,
            1,
        )

    def test_rejects_non_craft_decision(
        self,
    ):
        self.tracker.update(
            Screen.SHOP,
            0.99,
        )

        decision = PlannerDecision(
            planner="market",
            action="SELL",
            base_priority=50,
            reason="test",
        )

        with self.assertRaises(
            ValueError
        ):
            self.planner.plan(
                decision
            )

    def test_requires_target_item(
        self,
    ):
        self.tracker.update(
            Screen.CRAFT,
            0.99,
        )

        decision = PlannerDecision(
            planner="craft",
            action="CRAFT",
            base_priority=50,
            reason="test",
        )

        with self.assertRaises(
            ValueError
        ):
            self.planner.plan(
                decision
            )

    def test_requires_reliable_navigation_state(
        self,
    ):
        decision = self.make_decision()

        with self.assertRaises(
            RuntimeError
        ):
            self.planner.plan(
                decision
            )


if __name__ == "__main__":
    unittest.main()