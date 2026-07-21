import unittest

import cv2
import numpy as np

from core.screen_state import ScreenState
from vision.screen_detector import ScreenDetector
from vision.template_matcher import TemplateMatcher
from vision.vision_engine import VisionEngine
from vision.vision_validator import VisionValidator


class TestVisionValidator(unittest.TestCase):
    def test_expected_screen(self):
        template = np.zeros((18, 26, 3), dtype=np.uint8)
        cv2.rectangle(template, (2, 2), (23, 15), (255, 255, 255), -1)
        cv2.circle(template, (13, 9), 4, (0, 0, 0), -1)

        screen = np.zeros((90, 130, 3), dtype=np.uint8)
        screen[30:48, 50:76] = template

        engine = VisionEngine(
            detector=ScreenDetector(
                matcher=TemplateMatcher(threshold=0.90),
                templates={"town": template},
            )
        )
        validator = VisionValidator(engine, lambda: screen)

        self.assertTrue(validator.validate(ScreenState.TOWN))
        self.assertFalse(validator.validate(ScreenState.LOADING))


if __name__ == "__main__":
    unittest.main()
