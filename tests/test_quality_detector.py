from vision.capture import screenshot
from vision.inventory_card_locator import InventoryCardLocator
from vision.inventory_card_regions import InventoryCardRegionLocator
from vision.inventory_detector import InventoryDetector
from vision.quality_detector import QualityDetector
from vision.tier_badge_detector import TierBadgeDetector
PANEL_WIDTH_RATIO=2.58;CONTENT_TOP_OFFSET=85;CONTENT_BOTTOM_MARGIN=70
if __name__=="__main__":
    frame=screenshot();inventory=InventoryDetector().detect(image=frame)
    if inventory is None:print("沒有找到 Inventory")
    else:
        h,w=frame.shape[:2];left=inventory["x"];top=inventory["y"]+inventory["height"]+CONTENT_TOP_OFFSET;right=min(left+round(inventory["width"]*PANEL_WIDTH_RATIO),w-1);bottom=h-CONTENT_BOTTOM_MARGIN;badges=TierBadgeDetector().detect(frame,left,top,right,bottom);cards=InventoryCardLocator().locate(badges,left,right,bottom);rl=InventoryCardRegionLocator();qd=QualityDetector()
        for card in cards:
            r=qd.detect(frame,rl.locate(card).name);print(f"R{card.row}C{card.column} quality={r.quality.value:<10} confidence={r.confidence:.3f} ratios={r.ratios}")
