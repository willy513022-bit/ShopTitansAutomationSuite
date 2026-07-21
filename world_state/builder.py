from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, Optional

from vision.notification_models import (
    NotificationCategory,
    NotificationDetection,
    SemanticNotification,
)
from vision.notification_parser import NotificationParser
from vision.popup_models import PopupDetection, PopupState
from vision.popup_priority import PopupPriorityResolver

from .inventory_state import InventoryState
from .notification_state import NotificationState
from .production_state import ProductionState
from .recipe_state import RecipeState
from .world_state import WorldState


class WorldStateBuilder:
    """Build a planner-safe snapshot from raw Vision observations.

    The builder is the boundary between visual detections and the rest of the
    agent. It parses notification semantics, resolves popup priority, freezes
    mutable inputs, and stamps a single observation time.
    """

    def __init__(
        self,
        notification_parser: Optional[NotificationParser] = None,
        popup_resolver: Optional[PopupPriorityResolver] = None,
    ) -> None:
        self.notification_parser = notification_parser or NotificationParser()
        self.popup_resolver = popup_resolver or PopupPriorityResolver()

    def build(
        self,
        *,
        notification_detections: Iterable[NotificationDetection] = (),
        popup_detections: Iterable[PopupDetection] = (),
        inventory: Optional[InventoryState] = None,
        production: Optional[ProductionState] = None,
        recipes: Iterable[RecipeState] = (),
        screen: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
        observed_at: Optional[datetime] = None,
    ) -> WorldState:
        notifications = self._build_notifications(notification_detections)
        popup = self.popup_resolver.select(tuple(popup_detections))
        return WorldState(
            notifications=notifications,
            popup=popup,
            inventory=inventory,
            production=production,
            recipes=tuple(recipes),
            screen=screen,
            metadata=dict(metadata or {}),
            observed_at=observed_at or datetime.now(timezone.utc),
        )

    def build_from_semantics(
        self,
        *,
        notifications: Iterable[SemanticNotification] = (),
        popup: Optional[PopupState] = None,
        inventory: Optional[InventoryState] = None,
        production: Optional[ProductionState] = None,
        recipes: Iterable[RecipeState] = (),
        screen: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
        observed_at: Optional[datetime] = None,
    ) -> WorldState:
        mapped: dict[NotificationCategory, SemanticNotification] = {}
        for value in notifications:
            category = self._semantic_category(value)
            current = mapped.get(category)
            if current is None or value.confidence > current.confidence:
                mapped[category] = value
        return WorldState(
            notifications=NotificationState(mapped),
            popup=popup,
            inventory=inventory,
            production=production,
            recipes=tuple(recipes),
            screen=screen,
            metadata=dict(metadata or {}),
            observed_at=observed_at or datetime.now(timezone.utc),
        )

    def _build_notifications(
        self,
        detections: Iterable[NotificationDetection],
    ) -> NotificationState:
        winners: dict[NotificationCategory, NotificationDetection] = {}
        for detection in detections:
            current = winners.get(detection.category)
            if current is None or detection.confidence > current.confidence:
                winners[detection.category] = detection
        parsed = {
            category: self.notification_parser.parse(detection)
            for category, detection in winners.items()
        }
        return NotificationState(parsed)

    @staticmethod
    def _semantic_category(value: SemanticNotification) -> NotificationCategory:
        category = getattr(value, "category", None)
        if isinstance(category, NotificationCategory):
            return category
        return NotificationCategory.QUEST
