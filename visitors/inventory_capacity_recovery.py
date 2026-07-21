from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InventoryCandidate:
    item_id: str
    item_name: str
    quantity: int
    unit_value: int
    reserved_quantity: int = 0
    fusion_reserved_quantity: int = 0
    hero_reserved_quantity: int = 0
    precraft_reserved_quantity: int = 0


class InventoryCapacityRecovery:
    def choose_items_to_sell(
        self,
        candidates: list[InventoryCandidate],
        slots_needed: int,
    ) -> list[InventoryCandidate]:
        safe_candidates = []

        for candidate in candidates:
            protected = (
                candidate.reserved_quantity
                + candidate.fusion_reserved_quantity
                + candidate.hero_reserved_quantity
                + candidate.precraft_reserved_quantity
            )

            if candidate.quantity - protected <= 0:
                continue

            safe_candidates.append(candidate)

        safe_candidates.sort(
            key=lambda item: (
                item.unit_value,
                -item.quantity,
            )
        )

        return safe_candidates[:slots_needed]
