from models.craft import StockTarget
from models.inventory import InventorySnapshot
from services.craft_planner import CraftPlanner
class InventoryStrategy:
    def __init__(self,planner=None):self.planner=planner or CraftPlanner()
    def build_craft_queue(self,snapshot:InventorySnapshot,targets:list[StockTarget]):return self.planner.build_queue(snapshot,targets)
