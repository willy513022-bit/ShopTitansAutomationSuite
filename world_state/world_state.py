from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping, Optional, Tuple

from vision.popup_models import PopupState

from .inventory_state import InventoryState
from .notification_state import NotificationState
from .production_state import ProductionState
from .recipe_state import RecipeState


@dataclass(frozen=True, slots=True)
class WorldState:
    """Single immutable snapshot consumed by planners and schedulers."""

    notifications: NotificationState = field(default_factory=NotificationState)
    popup: Optional[PopupState] = None
    inventory: Optional[InventoryState] = None
    production: Optional[ProductionState] = None
    recipes: Tuple[RecipeState, ...] = ()
    screen: Optional[str] = None
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")
        recipes = tuple(self.recipes)
        if any(not isinstance(recipe, RecipeState) for recipe in recipes):
            raise TypeError("recipes must contain RecipeState values")
        screen = self.screen.strip() if isinstance(self.screen, str) else self.screen
        if screen == "":
            screen = None
        object.__setattr__(self, "recipes", recipes)
        object.__setattr__(self, "screen", screen)
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def has_blocking_popup(self) -> bool:
        return bool(self.popup and self.popup.blocking)

    @property
    def safe_for_gameplay(self) -> bool:
        return not self.has_blocking_popup
