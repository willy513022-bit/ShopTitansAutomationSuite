import unittest

import cv2
import numpy as np

from vision.screen_detector import ScreenDetector
from vision.template_matcher import TemplateMatcher


def make_template(kind: int) -> np.ndarray:
    image = np.zeros((24, 32, 3), dtype=np.uint8)
    if kind == 1:
        cv2.rectangle(image, (3, 3), (28, 20), (255, 255, 255), -1)
        cv2.line(image, (3, 3), (28, 20), (0, 0, 0), 2)
    else:
        cv2.circle(image, (16, 12), 9, (255, 255, 255), -1)
        cv2.line(image, (7, 12), (25, 12), (0, 0, 0), 2)
    return image


class TestScreenDetector(unittest.TestCase):
    def test_best_screen_wins(self):
        town = make_template(1)
        disconnected = make_template(2)

        screen = np.zeros((140, 180, 3), dtype=np.uint8)
        screen[50:74, 80:112] = disconnected

        detector = ScreenDetector(
            matcher=TemplateMatcher(threshold=0.90),
            templates={
                "town": town,
                "disconnected": disconnected,
            },
        )
        result = detector.detect(screen)

        self.assertIsNotNone(result)
        self.assertEqual(result.screen_name, "disconnected")


if __name__ == "__main__":
    unittest.main()
