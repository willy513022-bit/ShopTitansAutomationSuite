from __future__ import annotations

from dataclasses import dataclass

from ai.game_state import GameState
from inventory.manager import InventoryManager, inventory_manager
from models.inventory import InventorySnapshot


@dataclass(frozen=True)
class InventoryStateSummary:
    stack_count: int
    total_quantity: int


class InventoryStateProvider:
    def __init__(
        self,
        manager: InventoryManager = inventory_manager,
    ) -> None:
        self.manager = manager

    def get_snapshot(self) -> InventorySnapshot:
        return self.manager.snapshot

    def apply(
        self,
        state: GameState,
    ) -> None:
        snapshot = self.get_snapshot()

        state.metadata["inventory_snapshot"] = snapshot
        state.metadata["inventory_summary"] = (
            InventoryStateSummary(
                stack_count=len(snapshot.stacks),
                total_quantity=sum(
                    stack.quantity
                    for stack in snapshot.stacks
                ),
            )
        )
