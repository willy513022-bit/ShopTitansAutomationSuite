from dataclasses import dataclass
from models.quality import Quality
from vision.inventory_reader import InventoryReadResult

@dataclass(frozen=True)
class InventoryCardKey:
    item_id:str; item_name:str; quality:Quality; quantity:int
@dataclass(frozen=True)
class InventoryOverlapResult:
    overlap_count:int; new_items:list[InventoryCardKey]

class InventoryOverlapMatcher:
    def build_keys(self,results:list[InventoryReadResult]):
        return [InventoryCardKey(r.item_id,r.item_name,r.quality,r.quantity) for r in results if r.item_id is not None and r.item_name is not None and r.quantity is not None]
    def find_overlap(self,previous,current):
        if not previous:return InventoryOverlapResult(0,current.copy())
        if not current:return InventoryOverlapResult(0,[])
        overlap=0
        for size in range(min(len(previous),len(current)),0,-1):
            if previous[-size:]==current[:size]:overlap=size;break
        return InventoryOverlapResult(overlap,current[overlap:])
