from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from .screen import Screen


@dataclass(frozen=True)
class ScreenObservation:
    screen: Screen
    confidence: float
    observed_at: datetime


@dataclass
class NavigationStateTracker:
    current_screen: Screen = Screen.UNKNOWN
    confidence: float = 0.0
    history: list[ScreenObservation] = field(default_factory=list)

    def update(
        self,
        screen: Screen,
        confidence: float,
    ) -> ScreenObservation:
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")

        observation = ScreenObservation(
            screen=screen,
            confidence=confidence,
            observed_at=datetime.now(timezone.utc),
        )
        self.current_screen = screen
        self.confidence = confidence
        self.history.append(observation)
        return observation

    def is_reliable(self, minimum_confidence: float = 0.80) -> bool:
        return (
            self.current_screen != Screen.UNKNOWN
            and self.confidence >= minimum_confidence
        )

    def last(self) -> ScreenObservation | None:
        return self.history[-1] if self.history else None
