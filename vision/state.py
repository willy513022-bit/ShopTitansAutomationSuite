from __future__ import annotations

from dataclasses import dataclass

from navigation.screen import Screen


@dataclass(frozen=True)
class VisionState:
    screen: Screen
    screen_confidence: float

    production_mode: str | None = None
    queue_remaining: int | None = None
    completed_items: int | None = None
    gold: int | None = None

    def validate(self) -> None:
        if not 0.0 <= self.screen_confidence <= 1.0:
            raise ValueError("screen_confidence must be between 0 and 1")
        if self.queue_remaining is not None and self.queue_remaining < 0:
            raise ValueError("queue_remaining cannot be negative")
        if self.completed_items is not None and self.completed_items < 0:
            raise ValueError("completed_items cannot be negative")
        if self.gold is not None and self.gold < 0:
            raise ValueError("gold cannot be negative")
