from dataclasses import dataclass
from models.quality import Quality

@dataclass(frozen=True)
class StockTarget:
    item_id: str
    target_quantity: int
    quality: Quality = Quality.NORMAL
    safety_stock: int = 0
    priority: int = 0

@dataclass(frozen=True)
class CraftDemand:
    item_id: str
    item_name: str
    required_quantity: int
    current_quantity: int
    shortage: int
    precraft_demand: int
    safety_stock: int
    priority: int

@dataclass(frozen=True)
class CraftQueueItem:
    item_id: str
    item_name: str
    quantity: int
    priority: int
