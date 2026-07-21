from inventory.manager import InventoryManager,inventory_manager
from models.inventory import InventoryItemKey,InventoryStack
from vision.inventory_full_scanner import InventoryFullScanner
class InventoryController:
    def __init__(self,manager:InventoryManager=inventory_manager):self.manager=manager
    def scan_and_sync(self):
        summary=InventoryFullScanner().scan(); stacks=[InventoryStack(InventoryItemKey(i.item_id,i.quality),i.item_name,i.quantity) for i in summary.items];self.manager.replace_snapshot(stacks)
