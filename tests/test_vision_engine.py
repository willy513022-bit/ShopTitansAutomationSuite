import unittest

import cv2
import numpy as np

from core.screen_state import ScreenState
from vision.screen_detector import ScreenDetector
from vision.template_matcher import TemplateMatcher
from vision.vision_engine import VisionEngine


class TestVisionEngine(unittest.TestCase):
    def test_analysis(self):
        template = np.zeros((20, 30, 3), dtype=np.uint8)
        cv2.rectangle(template, (2, 2), (27, 17), (255, 255, 255), -1)
        cv2.line(template, (2, 17), (27, 2), (0, 0, 0), 2)

        screen = np.zeros((100, 150, 3), dtype=np.uint8)
        screen[40:60, 65:95] = template

        detector = ScreenDetector(
            matcher=TemplateMatcher(threshold=0.90),
            templates={"welcome_back": template},
        )
        engine = VisionEngine(detector=detector)
        result = engine.analyze(screen)

        self.assertEqual(result.screen_state, ScreenState.WELCOME_BACK)
        self.assertGreaterEqual(result.confidence, 0.90)


if __name__ == "__main__":
    unittest.main()
