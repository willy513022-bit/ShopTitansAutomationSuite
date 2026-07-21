import unittest

from vision.notification_models import (
    NotificationCategory,
    NotificationDetection,
    ProductionNotification,
    QuestNotification,
)


class TestNotificationModels(unittest.TestCase):
    def test_detection_accepts_plus(self):
        result = NotificationDetection(
            category=NotificationCategory.CRAFT,
            badge=" + ",
            confidence=0.9,
            icon_confidence=0.95,
            badge_confidence=0.9,
        )
        self.assertEqual(result.badge, "+")

    def test_detection_rejects_unknown_badge(self):
        with self.assertRaises(ValueError):
            NotificationDetection(
                category=NotificationCategory.CRAFT,
                badge="?",
                confidence=0.9,
                icon_confidence=0.9,
                badge_confidence=0.9,
            )

    def test_production_category_validation(self):
        with self.assertRaises(ValueError):
            ProductionNotification(
                category=NotificationCategory.QUEST,
                finished_jobs=1,
                empty_slot_available=False,
                confidence=0.8,
            )

    def test_quest_count_validation(self):
        with self.assertRaises(ValueError):
            QuestNotification(
                notification_count=-1,
                new_available=False,
                confidence=0.8,
            )


if __name__ == "__main__":
    unittest.main()
