import unittest

from core.planner_decision import PlannerDecision
from navigation import (
    NavigationStateTracker,
    Navigator,
    Screen,
    build_default_screen_graph,
)
from runtime.craft_execution import (
    CraftExecutionPlanner,
    CraftExecutionStep,
    CraftExecutionStepKind,
)
from runtime.navigation_dry_run_executor import (
    NavigationDryRunExecutor,
)


class NavigationDryRunExecutorTests(
    unittest.TestCase
):
    def make_plan(
        self,
        start_screen=Screen.SHOP,
    ):
        tracker = NavigationStateTracker()

        tracker.update(
            start_screen,
            0.99,
        )

        navigator = Navigator(
            build_default_screen_graph(),
            tracker,
        )

        planner = CraftExecutionPlanner(
            navigator
        )

        decision = PlannerDecision(
            planner="blueprint",
            action="CRAFT",
            base_priority=55,
            reason="test",
            payload={
                "target_item":
                    "Bleakspire Roots",
                "requested_count": 1,
            },
        )

        return planner.plan(
            decision
        )

    def test_shop_to_craft_resolves_two_targets(
        self,
    ):
        plan = self.make_plan()

        result = (
            NavigationDryRunExecutor()
            .execute(plan)
        )

        self.assertEqual(
            result.navigation_step_count,
            2,
        )

        self.assertEqual(
            tuple(
                item.target_name
                for item
                in result.navigation_steps
            ),
            (
                "production_button",
                "craft_tab",
            ),
        )

    def test_first_step_is_open_production(
        self,
    ):
        plan = self.make_plan()

        result = (
            NavigationDryRunExecutor()
            .execute(plan)
        )

        first = result.navigation_steps[0]

        self.assertEqual(
            first.step_index,
            1,
        )

        self.assertEqual(
            first.target_name,
            "production_button",
        )

        self.assertFalse(
            first.executed
        )

        self.assertIn(
            "OPEN_PRODUCTION",
            first.description,
        )

    def test_second_step_is_switch_to_craft(
        self,
    ):
        plan = self.make_plan()

        result = (
            NavigationDryRunExecutor()
            .execute(plan)
        )

        second = result.navigation_steps[1]

        self.assertEqual(
            second.step_index,
            2,
        )

        self.assertEqual(
            second.target_name,
            "craft_tab",
        )

        self.assertIn(
            "SWITCH_TO_CRAFT",
            second.description,
        )

    def test_already_on_craft_has_no_navigation(
        self,
    ):
        plan = self.make_plan(
            Screen.CRAFT
        )

        result = (
            NavigationDryRunExecutor()
            .execute(plan)
        )

        self.assertEqual(
            result.navigation_step_count,
            0,
        )

        self.assertEqual(
            result.navigation_steps,
            (),
        )

    def test_non_navigation_steps_are_ignored(
        self,
    ):
        plan = self.make_plan()

        result = (
            NavigationDryRunExecutor()
            .execute(plan)
        )

        self.assertEqual(
            len(plan.steps),
            6,
        )

        self.assertEqual(
            result.navigation_step_count,
            2,
        )

    def test_navigation_step_keeps_transition(
        self,
    ):
        plan = self.make_plan()

        first = plan.steps[0]

        self.assertEqual(
            first.kind,
            CraftExecutionStepKind.NAVIGATE,
        )

        self.assertIsNotNone(
            first.transition
        )

        assert first.transition is not None

        self.assertEqual(
            first.transition.source,
            Screen.SHOP,
        )

        self.assertEqual(
            first.transition.target,
            Screen.PRODUCTION,
        )

    def test_navigate_step_requires_transition(
        self,
    ):
        with self.assertRaises(
            ValueError
        ):
            CraftExecutionStep(
                kind=(
                    CraftExecutionStepKind
                    .NAVIGATE
                ),
                description="invalid",
            )

    def test_non_navigation_cannot_have_transition(
        self,
    ):
        plan = self.make_plan()

        transition = (
            plan.navigation
            .transitions[0]
        )

        with self.assertRaises(
            ValueError
        ):
            CraftExecutionStep(
                kind=(
                    CraftExecutionStepKind
                    .FIND_ITEM
                ),
                description="invalid",
                transition=transition,
            )

    def test_rejects_non_plan(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            NavigationDryRunExecutor().execute(
                object()
            )


if __name__ == "__main__":
    unittest.main()