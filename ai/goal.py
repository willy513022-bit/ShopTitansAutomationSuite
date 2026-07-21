from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class GoalType(str, Enum):
    COLLECTION = "collection"
    INVENTORY = "inventory"
    PROFIT = "profit"
    EXPERIENCE = "experience"
    QUEST_MATERIAL = "quest_material"
    EVENT = "event"


@dataclass
class Goal:
    goal_id: str
    goal_type: GoalType
    priority: int
    enabled: bool = True
    target: dict[str, Any] = field(
        default_factory=dict
    )
    progress: dict[str, Any] = field(
        default_factory=dict
    )
