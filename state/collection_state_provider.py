from __future__ import annotations

from dataclasses import dataclass, field

from ai.game_state import (
    CollectionTask,
    GameState,
)
from models.quality import Quality


@dataclass(frozen=True)
class CollectionGoalConfig:
    task_id: str
    item_id: str
    item_name: str
    target_quality: Quality
    priority: int = 90
    missing_materials: tuple[str, ...] = field(
        default_factory=tuple
    )
    ready_to_donate: bool = False
    ready_to_fuse: bool = False
    ready_to_craft: bool = False


class CollectionStateProvider:
    def __init__(
        self,
        goals: list[CollectionGoalConfig] | None = None,
    ) -> None:
        self.goals = goals or []

    def apply(
        self,
        state: GameState,
    ) -> None:
        state.collection_tasks = [
            CollectionTask(
                task_id=goal.task_id,
                item_id=goal.item_id,
                item_name=goal.item_name,
                target_quality=goal.target_quality.value,
                ready_to_donate=goal.ready_to_donate,
                ready_to_fuse=goal.ready_to_fuse,
                ready_to_craft=goal.ready_to_craft,
                missing_materials=list(
                    goal.missing_materials
                ),
                priority=goal.priority,
            )
            for goal in self.goals
        ]
