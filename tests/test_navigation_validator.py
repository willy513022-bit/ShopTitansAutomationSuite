import unittest

from navigation import NavigationValidator, Screen


class TestNavigationValidator(unittest.TestCase):
    def setUp(self):
        self.validator = NavigationValidator()

    def test_arrival_success(self):
        result = self.validator.validate_arrival(
            Screen.CRAFT,
            Screen.CRAFT,
            0.94,
        )
        self.assertTrue(result.success)
        self.assertEqual(result.reason, "ARRIVED")

    def test_wrong_screen(self):
        result = self.validator.validate_arrival(
            Screen.CRAFT,
            Screen.FUSION,
            0.94,
        )
        self.assertFalse(result.success)
        self.assertEqual(result.reason, "WRONG_SCREEN")

    def test_low_confidence(self):
        result = self.validator.validate_arrival(
            Screen.CRAFT,
            Screen.CRAFT,
            0.50,
        )
        self.assertFalse(result.success)
        self.assertEqual(result.reason, "LOW_CONFIDENCE")
