from __future__ import annotations

from dataclasses import dataclass, field

from ai.game_state import (
    CurrencyState,
    GameState,
)


@dataclass(frozen=True)
class CurrencySnapshot:
    gold: int = 0
    gems: int = 0
    special_currency: dict[str, int] = field(
        default_factory=dict
    )


class CurrencyStateProvider:
    def __init__(
        self,
        snapshot: CurrencySnapshot | None = None,
    ) -> None:
        self.snapshot = (
            snapshot
            or CurrencySnapshot()
        )

    def apply(
        self,
        state: GameState,
    ) -> None:
        state.currencies = CurrencyState(
            gold=self.snapshot.gold,
            gems=self.snapshot.gems,
            special_currency=dict(
                self.snapshot.special_currency
            ),
        )
