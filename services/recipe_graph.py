from collections import defaultdict
from services.game_data_service import GameDataService, game_data_service

class RecipeDependencyGraph:
    def __init__(self, game_data: GameDataService = game_data_service):
        self.game_data = game_data
        self.rebuild()

    def rebuild(self):
        self._dependencies = {item.item_id: {i.item_id: i.quantity for i in item.ingredients if i.resource_type == "item" and i.item_id is not None} for item in self.game_data.get_all()}

    def direct_dependencies(self, item_id: str): return dict(self._dependencies.get(item_id, {}))

    def expand_item_requirements(self, item_id: str, quantity: int):
        totals = defaultdict(int)
        self._expand(item_id, quantity, totals, ())
        totals.pop(item_id, None)
        return dict(totals)

    def _expand(self, item_id, quantity, totals, path):
        if item_id in path: raise ValueError("Recipe dependency cycle: " + " -> ".join((*path, item_id)))
        totals[item_id] += quantity
        next_path = (*path, item_id)
        for dependency_id, per_craft in self._dependencies.get(item_id, {}).items():
            self._expand(dependency_id, quantity * per_craft, totals, next_path)

recipe_graph = RecipeDependencyGraph()
