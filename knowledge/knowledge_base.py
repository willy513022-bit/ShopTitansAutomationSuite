from __future__ import annotations

from pathlib import Path

from knowledge.clickmap_registry import ClickMapRegistry
from knowledge.event_registry import EventRegistry
from knowledge.recipe_registry import RecipeRegistry
from knowledge.template_registry import TemplateRegistry


class GameKnowledgeBase:
    def __init__(self, data_root: str | Path):
        self.data_root = Path(data_root)
        self.events = EventRegistry()
        self.recipes = RecipeRegistry()
        self.templates = TemplateRegistry()
        self.clickmaps = ClickMapRegistry()

    def load(self) -> "GameKnowledgeBase":
        self.events.load_directory(self.data_root / "events")

        items_file = self.data_root / "recipes" / "items.json"
        if items_file.exists():
            self.recipes.load_file(items_file)

        templates_file = self.data_root / "templates" / "registry.json"
        if templates_file.exists():
            self.templates.load_file(templates_file)

        clickmap_directory = self.data_root / "clickmaps"
        if clickmap_directory.exists():
            for path in sorted(clickmap_directory.glob("*.json")):
                self.clickmaps.load_file(path)

        return self

    def summary(self) -> dict:
        return {
            "events": len(self.events),
            "recipes": len(self.recipes),
            "templates": len(self.templates),
            "clickmaps": len(self.clickmaps),
        }
