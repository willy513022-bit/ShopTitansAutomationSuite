from dataclasses import dataclass
from vision.tier_badge_detector import TierBadge

@dataclass(frozen=True)
class InventoryCard:
    row:int; column:int; x:int; y:int; width:int; height:int

class InventoryCardLocator:
    COLUMN_COUNT=3; CARD_TOP_FROM_BADGE=-20; CARD_WIDTH=195; CARD_HEIGHT=250
    def locate(self,badges:list[TierBadge],content_left:int,content_right:int,content_bottom:int):
        if not badges: return []
        column_width=(content_right-content_left)/self.COLUMN_COUNT; rows={}
        for badge in badges: rows.setdefault(badge.row,[]).append(badge)
        cards=[]
        for row_index,row_badges in rows.items():
            card_y=round(sum(b.center_y for b in row_badges)/len(row_badges))+self.CARD_TOP_FROM_BADGE
            if card_y+self.CARD_HEIGHT>content_bottom: continue
            for column in range(self.COLUMN_COUNT):
                cards.append(InventoryCard(row_index,column,round(content_left+column_width*column)+16,card_y,self.CARD_WIDTH,self.CARD_HEIGHT))
        cards.sort(key=lambda c:(c.row,c.column)); return cards
