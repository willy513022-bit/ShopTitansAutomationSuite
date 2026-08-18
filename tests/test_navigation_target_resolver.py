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

    def test_open_craft_target(self):
        target = self.resolver.resolve_action(
            TransitionAction.OPEN_CRAFT
        )

        self.assertEqual(
            target.target_name,
            "craft_button",
        )

    def test_open_fusion_target(self):
        target = self.resolver.resolve_action(
            TransitionAction.OPEN_FUSION
        )

        self.assertEqual(
            target.target_name,
            "fusion_button",
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
            target=Screen.CRAFT,
            action=(
                TransitionAction
                .OPEN_CRAFT
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
            TransitionAction.OPEN_CRAFT,
        )

        self.assertEqual(
            target.target_name,
            "craft_button",
        )

    def test_all_default_actions_are_registered(
        self,
    ):
        resolver = NavigationTargetResolver()

        for action in (
            TransitionAction.OPEN_CRAFT,
            TransitionAction.OPEN_FUSION,
            TransitionAction.BACK,
            TransitionAction.OPEN_QUEST,
            TransitionAction.OPEN_GUILD,
            TransitionAction.OPEN_PET,
            TransitionAction.OPEN_UPGRADE,
            TransitionAction.OPEN_KING,
            TransitionAction.CLOSE_MODAL,
        ):
            self.assertTrue(
                resolver.has_action(action),
                action.value,
            )

    def test_switch_actions_are_not_default_targets(
        self,
    ):
        self.assertFalse(
            self.resolver.has_action(
                TransitionAction.SWITCH_TO_CRAFT
            )
        )

        self.assertFalse(
            self.resolver.has_action(
                TransitionAction.SWITCH_TO_FUSION
            )
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
                TransitionAction.OPEN_CRAFT
            )

    def test_rejects_non_action(self):
        with self.assertRaises(
            TypeError
        ):
            self.resolver.resolve_action(
                "OPEN_CRAFT"
            )


if __name__ == "__main__":
    unittest.main()