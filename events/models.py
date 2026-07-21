from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EventTaskStatus(str, Enum):
    READY = "ready"
    BLOCKED_RESOURCE = "blocked_resource"
    WAITING_CRAFT = "waiting_craft"
    COMPLETED = "completed"


@dataclass(frozen=True)
class EventCraftOption:
    item_id: str
    item_name: str
    points: int
    craft_time_seconds: int
    resources_available: bool
    collection_conflict: bool = False
    hero_conflict: bool = False
