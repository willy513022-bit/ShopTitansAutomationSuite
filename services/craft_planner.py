from collections import defaultdict
from models.craft import CraftDemand, CraftQueueItem, StockTarget
from models.inventory import InventorySnapshot
from models.quality import Quality
from services.game_data_service import GameDataService, game_data_service
from services.recipe_graph import RecipeDependencyGraph, recipe_graph

class CraftPlanner:
    def __init__(self, game_data: GameDataService = game_data_service, graph: RecipeDependencyGraph = recipe_graph):
        self.game_data = game_data
        self.graph = graph

    def build_demands(self, snapshot: InventorySnapshot, targets: list[StockTarget]):
        precraft_demand = defaultdict(int)
        for target in targets:
            if target.quality != Quality.NORMAL: continue
            for dependency_id, quantity in self.graph.expand_item_requirements(target.item_id, target.target_quantity).items():
                precraft_demand[dependency_id] += quantity
        target_by_id = {target.item_id: target for target in targets}
        demands = []
        for item_id in set(target_by_id) | set(precraft_demand):
            target = target_by_id.get(item_id)
            base_target = target.target_quantity if target else 0
            safety_stock = target.safety_stock if target else 0
            priority = target.priority if target else 0
            pre_demand = precraft_demand.get(item_id, 0)
            required = base_target + safety_stock + pre_demand
            current = snapshot.quantity_of(item_id, Quality.NORMAL)
            shortage = max(0, required - current)
            item = self.game_data.get_by_id(item_id)
            demands.append(CraftDemand(item_id, item.name if item else item_id, required, current, shortage, pre_demand, safety_stock, priority))
        demands.sort(key=lambda d: (-d.priority, -d.shortage, d.item_name))
        return demands

    def build_queue(self, snapshot, targets):
        return [CraftQueueItem(d.item_id, d.item_name, d.shortage, d.priority) for d in self.build_demands(snapshot, targets) if d.shortage > 0]
