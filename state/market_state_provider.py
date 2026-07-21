from __future__ import annotations

from dataclasses import dataclass, field

from ai.game_state import (
    GameState,
    MarketOpportunity,
)


@dataclass(frozen=True)
class MarketSnapshot:
    opportunities: tuple[
        MarketOpportunity,
        ...
    ] = field(
        default_factory=tuple
    )


class MarketStateProvider:
    def __init__(
        self,
        snapshot: MarketSnapshot | None = None,
    ) -> None:
        self.snapshot = (
            snapshot
            or MarketSnapshot()
        )

    def apply(
        self,
        state: GameState,
    ) -> None:
        state.market_opportunities = list(
            self.snapshot.opportunities
        )
