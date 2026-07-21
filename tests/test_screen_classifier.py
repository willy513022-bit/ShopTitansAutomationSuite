import unittest

from core.screen_state import ScreenState
from vision.screen_classifier import ScreenClassifier


class TestScreenClassifier(unittest.TestCase):
    def test_known_state(self):
        classifier = ScreenClassifier()
        self.assertEqual(
            classifier.classify("limited_offer"),
            ScreenState.LIMITED_OFFER,
        )

    def test_unknown_state(self):
        classifier = ScreenClassifier()
        self.assertEqual(
            classifier.classify("not_registered"),
            ScreenState.UNKNOWN,
        )


if __name__ == "__main__":
    unittest.main()
