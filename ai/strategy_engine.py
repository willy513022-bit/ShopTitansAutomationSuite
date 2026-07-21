from __future__ import annotations

from ai.action import Action
from ai.game_state import GameState
from ai.priority_engine import PriorityEngine


class StrategyEngine:
    def __init__(
        self,
        priority_engine: PriorityEngine | None = None,
    ) -> None:
        self.priority_engine = (
            priority_engine
            or PriorityEngine()
        )

    def decide(
        self,
        state: GameState,
    ) -> Action:
        actions = (
            self.priority_engine
            .build_actions(state)
        )

        return actions[0]

    def rank(
        self,
        state: GameState,
    ) -> list[Action]:
        return (
            self.priority_engine
            .build_actions(state)
        )
