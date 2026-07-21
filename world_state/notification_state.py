from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping, Optional

from vision.notification_models import (
    NotificationCategory,
    ProductionNotification,
    QuestNotification,
    SemanticNotification,
)


@dataclass(frozen=True, slots=True)
class NotificationState:
    """Immutable semantic notification snapshot.

    At most one notification is retained per category. The builder resolves
    duplicate visual detections before creating this object.
    """

    values: Mapping[NotificationCategory, SemanticNotification] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        normalized: dict[NotificationCategory, SemanticNotification] = {}
        for category, value in self.values.items():
            key = (
                category
                if isinstance(category, NotificationCategory)
                else NotificationCategory(str(category).strip().lower())
            )
            if key in (NotificationCategory.CRAFT, NotificationCategory.FUSION):
                if not isinstance(value, ProductionNotification):
                    raise TypeError(f"{key.value} requires ProductionNotification")
                if value.category is not key:
                    raise ValueError("notification category does not match mapping key")
            elif key is NotificationCategory.QUEST:
                if not isinstance(value, QuestNotification):
                    raise TypeError("quest requires QuestNotification")
            normalized[key] = value
        object.__setattr__(self, "values", MappingProxyType(normalized))

    def get(self, category: NotificationCategory | str) -> Optional[SemanticNotification]:
        key = (
            category
            if isinstance(category, NotificationCategory)
            else NotificationCategory(str(category).strip().lower())
        )
        return self.values.get(key)

    @property
    def craft(self) -> Optional[ProductionNotification]:
        value = self.values.get(NotificationCategory.CRAFT)
        return value if isinstance(value, ProductionNotification) else None

    @property
    def fusion(self) -> Optional[ProductionNotification]:
        value = self.values.get(NotificationCategory.FUSION)
        return value if isinstance(value, ProductionNotification) else None

    @property
    def quest(self) -> Optional[QuestNotification]:
        value = self.values.get(NotificationCategory.QUEST)
        return value if isinstance(value, QuestNotification) else None

    @property
    def any_visible(self) -> bool:
        return bool(self.values)
