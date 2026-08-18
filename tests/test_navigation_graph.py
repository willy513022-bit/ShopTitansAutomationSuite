import unittest

from navigation import (
    Screen,
    TransitionAction,
    build_default_screen_graph,
)


class TestNavigationGraph(unittest.TestCase):
    def setUp(self):
        self.graph = build_default_screen_graph()

    def test_shop_to_craft_is_direct(self):
        path = self.graph.shortest_path(
            Screen.SHOP,
            Screen.CRAFT,
        )

        self.assertEqual(len(path), 1)
        self.assertEqual(
            path[0].source,
            Screen.SHOP,
        )
        self.assertEqual(
            path[0].target,
            Screen.CRAFT,
        )
        self.assertEqual(
            path[0].action,
            TransitionAction.OPEN_CRAFT,
        )

    def test_shop_to_fusion_is_direct(self):
        path = self.graph.shortest_path(
            Screen.SHOP,
            Screen.FUSION,
        )

        self.assertEqual(len(path), 1)
        self.assertEqual(
            path[0].source,
            Screen.SHOP,
        )
        self.assertEqual(
            path[0].target,
            Screen.FUSION,
        )
        self.assertEqual(
            path[0].action,
            TransitionAction.OPEN_FUSION,
        )

    def test_fusion_to_shop(self):
        path = self.graph.shortest_path(
            Screen.FUSION,
            Screen.SHOP,
        )

        self.assertEqual(len(path), 1)
        self.assertEqual(
            path[0].target,
            Screen.SHOP,
        )

    def test_same_screen_has_empty_path(self):
        self.assertEqual(
            self.graph.shortest_path(
                Screen.SHOP,
                Screen.SHOP,
            ),
            [],
        )

    def test_unknown_has_no_path(self):
        with self.assertRaises(LookupError):
            self.graph.shortest_path(
                Screen.UNKNOWN,
                Screen.SHOP,
            )


if __name__ == "__main__":
    unittest.main()