from __future__ import annotations

from ai.game_state import GameState
from state.provider_protocol import StateProvider


class GameStateBuilder:
    def __init__(
        self,
        providers: list[StateProvider] | None = None,
    ) -> None:
        self.providers = providers or []

    def add_provider(
        self,
        provider: StateProvider,
    ) -> "GameStateBuilder":
        self.providers.append(provider)
        return self

    def build(self) -> GameState:
        state = GameState()

        for provider in self.providers:
            provider.apply(state)

        return state
