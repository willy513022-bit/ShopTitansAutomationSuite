from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True, slots=True)
class RecipeState:
    item: str
    tier: int
    craft_time_seconds: float = 0.0
    materials: Mapping[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.item.strip():
            raise ValueError("item must not be empty")
        if self.tier < 1:
            raise ValueError("tier must be at least 1")
        if self.craft_time_seconds < 0:
            raise ValueError("craft_time_seconds must not be negative")
        object.__setattr__(self, "item", self.item.strip())
        object.__setattr__(
            self,
            "materials",
            MappingProxyType({str(k): max(0, int(v)) for k, v in self.materials.items()}),
        )
