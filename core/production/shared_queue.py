from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from core.account_capabilities import AccountCapabilities


class ProductionMode(str, Enum):
    CRAFT = "CRAFT"
    FUSION = "FUSION"


@dataclass(frozen=True)
class QueueObservation:
    """Vision/OCR observation of the shared Craft/Fusion queue."""

    remaining_slots: int
    mode: ProductionMode
    ready_to_collect: int = 0

    def validate(self) -> None:
        if self.remaining_slots < 0:
            raise ValueError("remaining_slots cannot be negative")
        if self.ready_to_collect < 0:
            raise ValueError("ready_to_collect cannot be negative")


@dataclass
class SharedProductionQueue:
    capabilities: AccountCapabilities
    observation: QueueObservation

    def __post_init__(self) -> None:
        self.capabilities.validate()
        self.observation.validate()
        if self.observation.remaining_slots > self.capacity:
            raise ValueError(
                "remaining_slots cannot exceed production queue capacity"
            )

    @property
    def capacity(self) -> int:
        return self.capabilities.production_queue_capacity

    @property
    def remaining_slots(self) -> int:
        return self.observation.remaining_slots

    @property
    def occupied_slots(self) -> int:
        return self.capacity - self.remaining_slots

    def can_schedule(self, count: int = 1) -> bool:
        if count < 0:
            raise ValueError("count cannot be negative")
        return self.remaining_slots >= count

    def should_collect_first(self) -> bool:
        return self.observation.ready_to_collect > 0

    def expected_remaining_after_collect(self, collected_count: int) -> int:
        if collected_count < 0:
            raise ValueError("collected_count cannot be negative")
        if collected_count > self.observation.ready_to_collect:
            raise ValueError("cannot collect more items than ready_to_collect")
        return min(self.capacity, self.remaining_slots + collected_count)

    def switch_mode(self, target: ProductionMode) -> QueueObservation:
        """Return the expected observation after a validated UI mode switch.

        Runtime/Vision must still verify that the displayed title matches target.
        """
        return QueueObservation(
            remaining_slots=self.observation.remaining_slots,
            mode=target,
            ready_to_collect=self.observation.ready_to_collect,
        )
