import unittest

from navigation import (
    NavigationStateTracker,
    Navigator,
    Screen,
    build_default_screen_graph,
)


class TestNavigator(unittest.TestCase):
    def setUp(self):
        self.tracker = NavigationStateTracker()
        self.navigator = Navigator(
            build_default_screen_graph(),
            self.tracker,
        )

    def test_plan_requires_reliable_screen(self):
        with self.assertRaises(RuntimeError):
            self.navigator.plan(Screen.SHOP)

    def test_plan_shop_to_craft(self):
        self.tracker.update(Screen.SHOP, 0.99)
        plan = self.navigator.plan(Screen.CRAFT)

        self.assertEqual(plan.start, Screen.SHOP)
        self.assertEqual(plan.target, Screen.CRAFT)
        self.assertEqual(plan.screens(), (
            Screen.SHOP,
            Screen.PRODUCTION,
            Screen.CRAFT,
        ))
        self.assertEqual(plan.total_cost, 2)

    def test_noop_plan(self):
        self.tracker.update(Screen.SHOP, 0.95)
        plan = self.navigator.plan(Screen.SHOP)
        self.assertTrue(plan.is_noop)
