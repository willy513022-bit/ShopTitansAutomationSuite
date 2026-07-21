from collections import defaultdict
from dataclasses import dataclass
from models.quality import Quality
from vision.inventory_reader import InventoryReadResult

@dataclass(frozen=True)
class InventoryPageItem:
    item_id:str; item_name:str; quality:Quality; quantity:int

class InventoryPageResult:
    def merge(self,results:list[InventoryReadResult]):
        quantities=defaultdict(int)
        for r in results:
            if r.item_id is None or r.item_name is None or r.quantity is None:continue
            quantities[(r.item_id,r.item_name,r.quality)]+=r.quantity
        items=[InventoryPageItem(iid,name,q,qty) for (iid,name,q),qty in quantities.items()]; items.sort(key=lambda i:(i.item_name,i.quality.value)); return items
