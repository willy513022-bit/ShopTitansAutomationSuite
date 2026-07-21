from __future__ import annotations

from dataclasses import dataclass, field

from ai.game_state import (
    GameState,
    QuestOption,
)


@dataclass(frozen=True)
class QuestSnapshot:
    options: tuple[QuestOption, ...] = field(
        default_factory=tuple
    )
    completed_quest_ids: tuple[str, ...] = field(
        default_factory=tuple
    )


class QuestStateProvider:
    def __init__(
        self,
        snapshot: QuestSnapshot | None = None,
    ) -> None:
        self.snapshot = (
            snapshot
            or QuestSnapshot()
        )

    def apply(
        self,
        state: GameState,
    ) -> None:
        state.quest_options = list(
            self.snapshot.options
        )
        state.completed_quest_ids = list(
            self.snapshot.completed_quest_ids
        )
