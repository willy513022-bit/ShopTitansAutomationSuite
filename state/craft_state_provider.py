from __future__ import annotations

from dataclasses import dataclass, field

from ai.game_state import (
    CraftJob,
    GameState,
)


@dataclass(frozen=True)
class CraftQueueSnapshot:
    jobs: tuple[CraftJob, ...] = field(
        default_factory=tuple
    )
    free_slots: int = 0
    completed_job_ids: tuple[str, ...] = field(
        default_factory=tuple
    )


class CraftStateProvider:
    def __init__(
        self,
        snapshot: CraftQueueSnapshot | None = None,
    ) -> None:
        self.snapshot = (
            snapshot
            or CraftQueueSnapshot()
        )

    def apply(
        self,
        state: GameState,
    ) -> None:
        state.craft_jobs = list(
            self.snapshot.jobs
        )
        state.free_craft_slots = (
            self.snapshot.free_slots
        )
        state.completed_craft_job_ids = list(
            self.snapshot.completed_job_ids
        )
