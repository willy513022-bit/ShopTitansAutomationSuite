import unittest

import cv2
import numpy as np

from vision.notification_detector import NotificationDetector, NotificationTemplateSet
from vision.notification_models import NotificationCategory
from vision.template_matcher import TemplateMatcher


def patterned_template(width, height, marker):
    image = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.rectangle(image, (1, 1), (width - 2, height - 2), (255, 255, 255), -1)
    cv2.line(image, (2, marker), (width - 3, height - 3), (0, 0, 0), 2)
    cv2.circle(image, (width // 2, height // 2), 2 + marker % 3, (40, 40, 40), -1)
    return image


class TestNotificationDetector(unittest.TestCase):
    def test_detects_registered_icon_and_best_badge(self):
        screen = np.zeros((160, 220, 3), dtype=np.uint8)
        icon = patterned_template(28, 24, 4)
        plus = patterned_template(16, 18, 5)
        seven = patterned_template(16, 18, 8)

        screen[30:54, 20:48] = icon
        screen[38:56, 52:68] = seven

        detector = NotificationDetector(
            templates={
                NotificationCategory.CRAFT: NotificationTemplateSet(
                    icon=icon,
                    badges={"+": plus, "7": seven},
                )
            },
            matcher=TemplateMatcher(threshold=0.95),
        )

        result = detector.detect_best(screen)

        self.assertIsNotNone(result)
        self.assertEqual(result.category, NotificationCategory.CRAFT)
        self.assertEqual(result.badge, "7")
        self.assertEqual(result.icon_location, (20, 30))
        self.assertEqual(result.badge_location, (52, 38))

    def test_returns_none_when_icon_is_missing(self):
        screen = np.zeros((100, 100, 3), dtype=np.uint8)
        icon = patterned_template(20, 20, 3)
        badge = patterned_template(12, 14, 6)
        detector = NotificationDetector(
            {
                "quest": NotificationTemplateSet(
                    icon=icon,
                    badges={"+": badge},
                )
            },
            matcher=TemplateMatcher(threshold=0.95),
        )

        self.assertIsNone(detector.detect_best(screen))

    def test_rejects_invalid_category(self):
        icon = patterned_template(20, 20, 3)
        badge = patterned_template(12, 14, 6)
        detector = NotificationDetector()
        with self.assertRaises(ValueError):
            detector.register(
                "mail",
                NotificationTemplateSet(icon=icon, badges={"+": badge}),
            )


if __name__ == "__main__":
    unittest.main()
