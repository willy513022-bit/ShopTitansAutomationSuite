from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class AccountCapabilities:
    """Values that may change as the player's account is upgraded."""

    production_queue_capacity: int = 10
    expedition_team_capacity: int = 8
    furniture_upgrade_slots: int = 2

    def validate(self) -> None:
        for field_name, value in asdict(self).items():
            if not isinstance(value, int) or value < 0:
                raise ValueError(f"{field_name} must be a non-negative integer")

    def update_from_observation(
        self,
        *,
        production_queue_capacity: int | None = None,
        expedition_team_capacity: int | None = None,
        furniture_upgrade_slots: int | None = None,
    ) -> None:
        updates = {
            "production_queue_capacity": production_queue_capacity,
            "expedition_team_capacity": expedition_team_capacity,
            "furniture_upgrade_slots": furniture_upgrade_slots,
        }
        for name, value in updates.items():
            if value is not None:
                setattr(self, name, value)
        self.validate()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
