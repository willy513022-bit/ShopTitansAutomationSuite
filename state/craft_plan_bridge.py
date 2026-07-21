from __future__ import annotations

from dataclasses import dataclass

from models.craft import StockTarget
from models.inventory import InventorySnapshot
from services.craft_planner import CraftPlanner


@dataclass(frozen=True)
class CraftPlanBridgeResult:
    queue_count: int
    queue: tuple[dict, ...]


class CraftPlanBridge:
    def __init__(
        self,
        planner: CraftPlanner | None = None,
    ) -> None:
        self.planner = (
            planner
            or CraftPlanner()
        )

    def build(
        self,
        snapshot: InventorySnapshot,
        targets: list[StockTarget],
    ) -> CraftPlanBridgeResult:
        queue_items = self.planner.build_queue(
            snapshot,
            targets,
        )

        payload = tuple(
            {
                "item_id": item.item_id,
                "item_name": item.item_name,
                "quantity": item.quantity,
                "priority": item.priority,
            }
            for item in queue_items
        )

        return CraftPlanBridgeResult(
            queue_count=len(payload),
            queue=payload,
        )
