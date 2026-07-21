from __future__ import annotations

from vision.notification_models import (
    NotificationCategory,
    NotificationDetection,
    ProductionNotification,
    QuestNotification,
    SemanticNotification,
)


class NotificationParser:
    """Convert raw visual notification detections into game semantics."""

    def parse(self, detection: NotificationDetection) -> SemanticNotification:
        if detection.category in (
            NotificationCategory.CRAFT,
            NotificationCategory.FUSION,
        ):
            return self._parse_production(detection)
        if detection.category is NotificationCategory.QUEST:
            return self._parse_quest(detection)
        raise ValueError(f"Unsupported notification category: {detection.category}")

    @staticmethod
    def _parse_production(
        detection: NotificationDetection,
    ) -> ProductionNotification:
        if detection.badge == "+":
            return ProductionNotification(
                category=detection.category,
                finished_jobs=0,
                empty_slot_available=True,
                confidence=detection.confidence,
            )

        return ProductionNotification(
            category=detection.category,
            finished_jobs=int(detection.badge),
            empty_slot_available=False,
            confidence=detection.confidence,
        )

    @staticmethod
    def _parse_quest(detection: NotificationDetection) -> QuestNotification:
        if detection.badge == "+":
            return QuestNotification(
                notification_count=0,
                new_available=True,
                confidence=detection.confidence,
            )

        return QuestNotification(
            notification_count=int(detection.badge),
            new_available=False,
            confidence=detection.confidence,
        )
