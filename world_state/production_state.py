from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProductionState:
    free_slots: int

    def __post_init__(self) -> None:
        if self.free_slots < 0:
            raise ValueError("free_slots must not be negative")
