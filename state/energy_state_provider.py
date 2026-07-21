from __future__ import annotations

from dataclasses import dataclass

from ai.game_state import (
    EnergyState,
    GameState,
)


@dataclass(frozen=True)
class EnergySnapshot:
    current: int
    maximum: int


class EnergyStateProvider:
    def __init__(
        self,
        snapshot: EnergySnapshot | None = None,
    ) -> None:
        self.snapshot = (
            snapshot
            or EnergySnapshot(
                current=0,
                maximum=1,
            )
        )

    def apply(
        self,
        state: GameState,
    ) -> None:
        state.energy = EnergyState(
            current=self.snapshot.current,
            maximum=self.snapshot.maximum,
        )
