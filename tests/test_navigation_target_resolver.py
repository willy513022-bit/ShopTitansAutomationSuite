import unittest

from navigation import (
    Screen,
    Transition,
    TransitionAction,
)
from runtime.navigation_target_resolver import (
    NavigationTargetResolver,
)


class NavigationTargetResolverTests(
    unittest.TestCase
):
    def setUp(self):
        self.resolver = (
            NavigationTargetResolver()
        )

    def test_open_production_target(self):
        target = self.resolver.resolve_action(
            TransitionAction.OPEN_PRODUCTION
        )

        self.assertEqual(
            target.target_name,
            "production_button",
        )

    def test_switch_to_craft_target(self):
        target = self.resolver.resolve_action(
            TransitionAction.SWITCH_TO_CRAFT
        )

        self.assertEqual(
            target.target_name,
            "craft_tab",
        )

    def test_switch_to_fusion_target(self):
        target = self.resolver.resolve_action(
            TransitionAction.SWITCH_TO_FUSION
        )

        self.assertEqual(
            target.target_name,
            "fusion_tab",
        )

    def test_back_target(self):
        target = self.resolver.resolve_action(
            TransitionAction.BACK
        )

        self.assertEqual(
            target.target_name,
            "back_button",
        )

    def test_resolve_transition(self):
        transition = Transition(
            source=Screen.SHOP,
            target=Screen.PRODUCTION,
            action=(
                TransitionAction
                .OPEN_PRODUCTION
            ),
        )

        target = (
            self.resolver
            .resolve_transition(
                transition
            )
        )

        self.assertEqual(
            target.action,
            TransitionAction.OPEN_PRODUCTION,
        )

        self.assertEqual(
            target.target_name,
            "production_button",
        )

    def test_all_default_actions_are_registered(
        self,
    ):
        for action in TransitionAction:
            self.assertTrue(
                self.resolver.has_action(
                    action
                ),
                action.value,
            )

    def test_custom_mapping_can_be_used(self):
        resolver = NavigationTargetResolver(
            {
                TransitionAction.BACK:
                    "custom_back",
            }
        )

        target = resolver.resolve_action(
            TransitionAction.BACK
        )

        self.assertEqual(
            target.target_name,
            "custom_back",
        )

    def test_unregistered_action_raises(
        self,
    ):
        resolver = NavigationTargetResolver(
            {
                TransitionAction.BACK:
                    "back_button",
            }
        )

        with self.assertRaises(KeyError):
            resolver.resolve_action(
                TransitionAction.OPEN_PRODUCTION
            )

    def test_rejects_non_action(self):
        with self.assertRaises(
            TypeError
        ):
            self.resolver.resolve_action(
                "OPEN_PRODUCTION"
            )


if __name__ == "__main__":
    unittest.main()