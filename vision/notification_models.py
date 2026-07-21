from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Optional


class NotificationCategory(str, Enum):
    """Notification families currently supported by Shop Titans."""

    CRAFT = "craft"
    FUSION = "fusion"
    QUEST = "quest"


@dataclass(frozen=True)
class NotificationDetection:
    """Raw visual result produced by ``NotificationDetector``.

    ``badge`` intentionally remains text because ``+`` has category-specific
    meaning and must not be converted into a number by the vision layer.
    """

    category: NotificationCategory
    badge: str
    confidence: float
    icon_confidence: float
    badge_confidence: float
    icon_location: Optional[tuple[int, int]] = None
    badge_location: Optional[tuple[int, int]] = None
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        badge = self.badge.strip()
        if not badge:
            raise ValueError("badge is required")
        if badge != "+" and not badge.isdigit():
            raise ValueError("badge must be '+' or a non-negative integer string")
        for name, value in (
            ("confidence", self.confidence),
            ("icon_confidence", self.icon_confidence),
            ("badge_confidence", self.badge_confidence),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
        object.__setattr__(self, "badge", badge)


@dataclass(frozen=True)
class ProductionNotification:
    """Semantic notification for Craft or Fusion."""

    category: NotificationCategory
    finished_jobs: int
    empty_slot_available: bool
    confidence: float

    def __post_init__(self) -> None:
        if self.category not in (
            NotificationCategory.CRAFT,
            NotificationCategory.FUSION,
        ):
            raise ValueError("ProductionNotification category must be craft or fusion")
        if self.finished_jobs < 0:
            raise ValueError("finished_jobs must be non-negative")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class QuestNotification:
    """Semantic quest notification.

    The quest ``+`` badge means a new quest is available. It is deliberately
    separate from ``notification_count``.
    """

    notification_count: int
    new_available: bool
    confidence: float

    def __post_init__(self) -> None:
        if self.notification_count < 0:
            raise ValueError("notification_count must be non-negative")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


SemanticNotification = ProductionNotification | QuestNotification
