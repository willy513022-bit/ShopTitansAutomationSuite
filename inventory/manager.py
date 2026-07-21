from models.inventory import InventorySnapshot,InventoryStack
class InventoryManager:
    def __init__(self):self.snapshot=InventorySnapshot(stacks=())
    def replace_snapshot(self,stacks:list[InventoryStack]):self.snapshot=InventorySnapshot(stacks=tuple(stacks))
inventory_manager=InventoryManager()
