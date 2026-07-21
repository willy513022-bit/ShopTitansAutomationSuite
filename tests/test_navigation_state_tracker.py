import unittest

from navigation import NavigationStateTracker, Screen


class TestNavigationStateTracker(unittest.TestCase):
    def test_update_and_reliability(self):
        tracker = NavigationStateTracker()
        self.assertFalse(tracker.is_reliable())

        tracker.update(Screen.SHOP, 0.95)

        self.assertEqual(tracker.current_screen, Screen.SHOP)
        self.assertTrue(tracker.is_reliable())
        self.assertEqual(len(tracker.history), 1)

    def test_invalid_confidence(self):
        tracker = NavigationStateTracker()
        with self.assertRaises(ValueError):
            tracker.update(Screen.SHOP, 1.2)
