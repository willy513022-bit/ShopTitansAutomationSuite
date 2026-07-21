from __future__ import annotations

from dataclasses import dataclass, field

from ai.game_state import (
    CustomerOffer,
    GameState,
)


@dataclass(frozen=True)
class CustomerSnapshot:
    offers: tuple[CustomerOffer, ...] = field(
        default_factory=tuple
    )


class CustomerStateProvider:
    def __init__(
        self,
        snapshot: CustomerSnapshot | None = None,
    ) -> None:
        self.snapshot = (
            snapshot
            or CustomerSnapshot()
        )

    def apply(
        self,
        state: GameState,
    ) -> None:
        state.customers = list(
            self.snapshot.offers
        )
