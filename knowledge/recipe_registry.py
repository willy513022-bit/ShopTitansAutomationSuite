from __future__ import annotations

from pathlib import Path

from knowledge.errors import KnowledgeValidationError
from knowledge.json_store import JsonStore
from knowledge.validators import (
    require_int,
    require_list,
    require_mapping,
    require_string,
)


class RecipeRegistry:
    def __init__(self, store: JsonStore | None = None):
        self.store = store or JsonStore()
        self._items: dict[str, dict] = {}

    def load_file(self, path: str | Path) -> "RecipeRegistry":
        document = self.store.load(path)
        root = require_mapping(document, str(path))
        items = require_list(root.get("items"), f"{path}.items")

        for index, item in enumerate(items):
            self.register(item, source=f"{path}.items[{index}]")
        return self

    def register(self, document: dict, source: str = "<memory>") -> None:
        item = require_mapping(document, source)
        item_id = require_string(item, "item_id", source)
        require_string(item, "name", source)
        require_int(item, "tier", source, minimum=1)
        ingredients = require_list(item.get("ingredients", []), f"{source}.ingredients")

        for index, ingredient in enumerate(ingredients):
            ingredient_doc = require_mapping(
                ingredient,
                f"{source}.ingredients[{index}]",
            )
            require_string(
                ingredient_doc,
                "item_id",
                f"{source}.ingredients[{index}]",
            )
            require_int(
                ingredient_doc,
                "quantity",
                f"{source}.ingredients[{index}]",
                minimum=1,
            )

        if item_id in self._items:
            raise KnowledgeValidationError(f"Duplicate item_id: {item_id}")

        self._items[item_id] = dict(item)

    def get(self, item_id: str) -> dict | None:
        item = self._items.get(item_id)
        return None if item is None else dict(item)

    def dependencies(self, item_id: str) -> tuple[dict, ...]:
        item = self._items.get(item_id)
        if item is None:
            return ()
        return tuple(dict(entry) for entry in item.get("ingredients", []))

    def all(self) -> tuple[dict, ...]:
        return tuple(dict(item) for item in self._items.values())

    def __len__(self) -> int:
        return len(self._items)
