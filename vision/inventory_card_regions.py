from dataclasses import dataclass
from vision.inventory_card_locator import InventoryCard

@dataclass(frozen=True)
class CardRegion:
    row:int; column:int; x:int; y:int; width:int; height:int
@dataclass(frozen=True)
class InventoryCardRegions:
    name:CardRegion; quantity:CardRegion

class InventoryCardRegionLocator:
    def locate(self,card:InventoryCard):
        return InventoryCardRegions(
            CardRegion(card.row,card.column,card.x+round(card.width*0.08),card.y+round(card.height*0.42),round(card.width*0.84),round(card.height*0.14)),
            CardRegion(card.row,card.column,card.x+round(card.width*0.69),card.y+round(card.height*0.13),round(card.width*0.23),round(card.height*0.23)))
