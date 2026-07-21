from __future__ import annotations

from typing import Protocol

from ai.game_state import GameState


class StateProvider(Protocol):
    def apply(
        self,
        state: GameState,
    ) -> None:
        ...
