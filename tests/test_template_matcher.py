import unittest

import cv2
import numpy as np

from vision.template_matcher import TemplateMatcher


class TestTemplateMatcher(unittest.TestCase):
    def test_match_found(self):
        screen = np.zeros((120, 160, 3), dtype=np.uint8)
        template = np.zeros((20, 30, 3), dtype=np.uint8)

        cv2.rectangle(template, (2, 2), (27, 17), (255, 255, 255), -1)
        cv2.circle(template, (15, 10), 5, (0, 0, 0), -1)
        screen[45:65, 70:100] = template

        matcher = TemplateMatcher(threshold=0.90)
        result = matcher.match(screen, template, "sample")

        self.assertTrue(result.matched)
        self.assertEqual(result.location, (70, 45))
        self.assertGreaterEqual(result.confidence, 0.90)

    def test_template_larger_than_screen(self):
        screen = np.zeros((20, 20, 3), dtype=np.uint8)
        template = np.zeros((30, 30, 3), dtype=np.uint8)

        result = TemplateMatcher().match(screen, template)

        self.assertFalse(result.matched)
        self.assertEqual(result.confidence, 0.0)


if __name__ == "__main__":
    unittest.main()
