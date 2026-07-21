from dataclasses import dataclass
from models.quality import Quality

@dataclass(frozen=True)
class InventoryItemKey:
    item_id: str
    quality: Quality

@dataclass(frozen=True)
class InventoryStack:
    key: InventoryItemKey
    item_name: str
    quantity: int

@dataclass(frozen=True)
class InventorySnapshot:
    stacks: tuple[InventoryStack, ...]

    def quantity_of(self, item_id: str, quality: Quality = Quality.NORMAL) -> int:
        return sum(stack.quantity for stack in self.stacks if stack.key.item_id == item_id and stack.key.quality == quality)
