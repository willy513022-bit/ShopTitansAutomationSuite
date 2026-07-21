from dataclasses import dataclass, field

@dataclass(frozen=True)
class RecipeIngredient:
    item_id: str | None
    name: str
    quantity: int
    resource_type: str = "item"

@dataclass(frozen=True)
class GameItem:
    item_id: str
    name: str
    item_type: str
    tier: int
    craft_time_seconds: int
    base_value: int = 0
    ingredients: tuple[RecipeIngredient, ...] = field(default_factory=tuple)
