import unittest

from vision.notification_models import (
    NotificationCategory,
    NotificationDetection,
    ProductionNotification,
    QuestNotification,
)
from vision.notification_parser import NotificationParser


def raw(category, badge):
    return NotificationDetection(
        category=category,
        badge=badge,
        confidence=0.93,
        icon_confidence=0.97,
        badge_confidence=0.93,
    )


class TestNotificationParser(unittest.TestCase):
    def setUp(self):
        self.parser = NotificationParser()

    def test_craft_plus_means_empty_slot(self):
        result = self.parser.parse(raw(NotificationCategory.CRAFT, "+"))
        self.assertIsInstance(result, ProductionNotification)
        self.assertTrue(result.empty_slot_available)
        self.assertEqual(result.finished_jobs, 0)

    def test_fusion_number_means_finished_jobs(self):
        result = self.parser.parse(raw(NotificationCategory.FUSION, "10"))
        self.assertIsInstance(result, ProductionNotification)
        self.assertFalse(result.empty_slot_available)
        self.assertEqual(result.finished_jobs, 10)

    def test_quest_plus_means_new_quest(self):
        result = self.parser.parse(raw(NotificationCategory.QUEST, "+"))
        self.assertIsInstance(result, QuestNotification)
        self.assertTrue(result.new_available)
        self.assertEqual(result.notification_count, 0)

    def test_quest_number_means_count(self):
        result = self.parser.parse(raw(NotificationCategory.QUEST, "8"))
        self.assertFalse(result.new_available)
        self.assertEqual(result.notification_count, 8)


if __name__ == "__main__":
    unittest.main()
