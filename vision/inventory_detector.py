from pathlib import Path
import cv2
from vision.capture import screenshot
from vision.matcher import find_template

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = PROJECT_ROOT / "data" / "templates" / "inventory" / "header.png"

class InventoryDetector:
    def __init__(self, threshold: float = 0.90):
        self.threshold = threshold
        self.template = cv2.imread(str(TEMPLATE_PATH))
        if self.template is None: raise FileNotFoundError(f"找不到 Inventory 標題模板：{TEMPLATE_PATH}")

    def detect(self, image=None):
        if image is None: image = screenshot()
        if image is None: return None
        result = find_template(image, self.template, threshold=self.threshold)
        if result is None: return None
        location, score = result
        height, width = self.template.shape[:2]
        return {"x":location[0],"y":location[1],"width":width,"height":height,"score":score}
