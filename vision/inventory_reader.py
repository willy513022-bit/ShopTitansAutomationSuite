from dataclasses import dataclass
from models.quality import Quality
from services.item_name_matcher import ItemNameMatcher,item_name_matcher
from vision.inventory_card_locator import InventoryCard
from vision.inventory_card_regions import InventoryCardRegionLocator
from vision.inventory_ocr import InventoryOCR
from vision.quality_detector import QualityDetector

@dataclass(frozen=True)
class InventoryReadResult:
    row:int; column:int; raw_name:str; item_id:str|None; item_name:str|None; name_match_score:float; quality:Quality; quality_confidence:float; quantity:int|None

class InventoryReader:
    def __init__(self,ocr=None,name_matcher=None,quality_detector=None):
        self.ocr=ocr or InventoryOCR(); self.name_matcher=name_matcher or item_name_matcher; self.quality_detector=quality_detector or QualityDetector(); self.region_locator=InventoryCardRegionLocator()
    def read_cards(self,image,cards:list[InventoryCard]):
        results=[]
        for card in cards:
            regions=self.region_locator.locate(card); o=self.ocr.read_card(image,regions.name,regions.quantity); m=self.name_matcher.match(o.name_raw); q=self.quality_detector.detect(image,regions.name)
            results.append(InventoryReadResult(card.row,card.column,o.name_raw,m.item_id,m.matched_name,m.score,q.quality,q.confidence,o.quantity))
        return results
