from vision.capture import screenshot
from vision.inventory_detector import InventoryDetector
if __name__=="__main__":
    frame=screenshot();print(InventoryDetector().detect(image=frame) if frame is not None else "無法擷取 Shop Titans")
