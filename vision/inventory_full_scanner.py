import time
from collections import defaultdict
from dataclasses import dataclass
from models.quality import Quality
from vision.capture import screenshot
from vision.inventory_card_locator import InventoryCardLocator
from vision.inventory_detector import InventoryDetector
from vision.inventory_overlap import InventoryCardKey, InventoryOverlapMatcher
from vision.inventory_reader import InventoryReader
from vision.mouse import drag_mouse
from vision.tier_badge_detector import TierBadgeDetector
from vision.window_position import game_to_screen

PANEL_WIDTH_RATIO = 2.58
CONTENT_TOP_OFFSET = 85
CONTENT_BOTTOM_MARGIN = 70

@dataclass(frozen=True)
class InventoryScanItem:
    item_id: str
    item_name: str
    quality: Quality
    quantity: int

@dataclass(frozen=True)
class InventoryScanSummary:
    pages_scanned: int
    cards_scanned: int
    items: list[InventoryScanItem]

class InventoryFullScanner:
    def __init__(self, maximum_pages=150, no_new_page_limit=3):
        self.maximum_pages = maximum_pages
        self.no_new_page_limit = no_new_page_limit
        self.inventory_detector = InventoryDetector()
        self.badge_detector = TierBadgeDetector()
        self.card_locator = InventoryCardLocator()
        self.reader = InventoryReader()
        self.overlap_matcher = InventoryOverlapMatcher()

    def scan(self):
        print()
        print("開始完整掃描 Inventory")
        print("=" * 70)
        frame = screenshot()
        if frame is None:
            raise RuntimeError("無法擷取 Shop Titans 視窗")
        inventory = self.inventory_detector.detect(image=frame)
        if inventory is None:
            raise RuntimeError("沒有找到 Inventory")
        capture_height, capture_width = frame.shape[:2]
        content = self._get_content_area(frame, inventory)
        drag = self._get_drag_points(content, capture_width, capture_height)
        print("Inventory Drag")
        print("-" * 70)
        print("Start：", drag["start_x"], drag["start_y"])
        print("End  ：", drag["end_x"], drag["end_y"])
        print("Scanner 不反向拖曳回頂，避免縮小/關閉 Inventory。")

        all_cards = []
        previous = []
        pages = 0
        no_new = 0
        for page_number in range(1, self.maximum_pages + 1):
            frame = screenshot()
            if frame is None:
                break
            inventory = self.inventory_detector.detect(image=frame)
            if inventory is None:
                print("Inventory 消失，停止掃描")
                break
            content = self._get_content_area(frame, inventory)
            results = self._read_page(frame, content)
            current = self.overlap_matcher.build_keys(results)
            pages += 1
            print()
            print(f"[Page {page_number}]")
            print("辨識卡片：", len(current))
            if not current:
                no_new += 1
            elif not previous:
                all_cards.extend(current)
                print("第一頁新增：", len(current))
                no_new = 0
            else:
                overlap = self.overlap_matcher.find_overlap(previous, current)
                print("重疊卡片：", overlap.overlap_count)
                print("新增卡片：", len(overlap.new_items))
                if overlap.new_items:
                    all_cards.extend(overlap.new_items)
                    no_new = 0
                else:
                    no_new += 1
            for key in current:
                print(f"  {key.item_name:<28} {key.quality.value:<10} × {key.quantity}")
            if no_new >= self.no_new_page_limit:
                print("判定已到 Inventory 底部")
                break
            if current:
                previous = current
            self._drag_down(drag)
        return InventoryScanSummary(pages, len(all_cards), self._merge_cards(all_cards))

    def _get_drag_points(self, content, capture_width, capture_height):
        width = content["right"] - content["left"]
        height = content["bottom"] - content["top"]
        game_x = content["left"] + round(width * 0.50)
        start_y = content["top"] + round(height * 0.68)
        end_y = content["top"] + round(height * 0.42)
        start_x, start_screen_y = game_to_screen(game_x, start_y, capture_width, capture_height)
        end_x, end_screen_y = game_to_screen(game_x, end_y, capture_width, capture_height)
        return {"start_x": start_x, "start_y": start_screen_y, "end_x": end_x, "end_y": end_screen_y}

    @staticmethod
    def _drag_down(drag):
        drag_mouse(drag["start_x"], drag["start_y"], drag["end_x"], drag["end_y"], 0.55)
        time.sleep(1.2)

    @staticmethod
    def _get_content_area(frame, inventory):
        height, width = frame.shape[:2]
        left = inventory["x"]
        top = inventory["y"] + inventory["height"] + CONTENT_TOP_OFFSET
        return {
            "left": left,
            "top": top,
            "right": min(left + round(inventory["width"] * PANEL_WIDTH_RATIO), width - 1),
            "bottom": height - CONTENT_BOTTOM_MARGIN,
        }

    def _read_page(self, frame, content):
        badges = self.badge_detector.detect(frame, content["left"], content["top"], content["right"], content["bottom"])
        cards = self.card_locator.locate(badges, content["left"], content["right"], content["bottom"])
        return self.reader.read_cards(frame, cards)

    @staticmethod
    def _merge_cards(cards: list[InventoryCardKey]):
        quantities = defaultdict(int)
        for card in cards:
            quantities[(card.item_id, card.item_name, card.quality)] += card.quantity
        items = [InventoryScanItem(item_id, item_name, quality, quantity) for (item_id, item_name, quality), quantity in quantities.items()]
        items.sort(key=lambda item: (item.item_name, item.quality.value))
        return items
