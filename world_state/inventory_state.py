from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True, slots=True)
class InventoryState:
    items: Mapping[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        normalized = {str(name): max(0, int(quantity)) for name, quantity in self.items.items()}
        object.__setattr__(self, "items", MappingProxyType(normalized))

    def quantity(self, item: str) -> int:
        return self.items.get(item, 0)
