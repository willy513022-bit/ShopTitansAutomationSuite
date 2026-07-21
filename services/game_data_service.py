import json
from pathlib import Path
from models.game_item import GameItem, RecipeIngredient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GAME_DATA_DIR = PROJECT_ROOT / "data" / "game_data"

class GameDataService:
    def __init__(self) -> None:
        self._items_by_id = {}
        self._items_by_name = {}
        self.reload()

    def reload(self) -> None:
        with (GAME_DATA_DIR / "items.json").open("r", encoding="utf-8") as file:
            item_rows = json.load(file)
        with (GAME_DATA_DIR / "recipes.json").open("r", encoding="utf-8") as file:
            recipe_rows = json.load(file)
        recipes_by_id = {row["item_id"]: tuple(RecipeIngredient(item_id=i.get("item_id"), name=i["name"], quantity=int(i["quantity"]), resource_type=i.get("resource_type", "item")) for i in row.get("ingredients", [])) for row in recipe_rows}
        items = [GameItem(item_id=row["item_id"], name=row["name"], item_type=row.get("item_type", "Unknown"), tier=int(row.get("tier",0)), craft_time_seconds=int(row.get("craft_time_seconds",0)), base_value=int(row.get("base_value",0)), ingredients=recipes_by_id.get(row["item_id"], ())) for row in item_rows]
        self._items_by_id = {item.item_id: item for item in items}
        self._items_by_name = {item.name: item for item in items}

    def get_all(self): return list(self._items_by_id.values())
    def get_by_id(self, item_id: str): return self._items_by_id.get(item_id)
    def get_by_name(self, name: str): return self._items_by_name.get(name)

game_data_service = GameDataService()
