from __future__ import annotations

from pathlib import Path
from typing import Iterable

from knowledge.errors import KnowledgeValidationError
from knowledge.json_store import JsonStore
from knowledge.validators import (
    require_bool,
    require_int,
    require_list,
    require_mapping,
    require_string,
)


class EventRegistry:
    ALLOWED_CATEGORIES = {
        "interrupt",
        "daily",
        "activity",
        "recovery",
    }

    def __init__(self, store: JsonStore | None = None):
        self.store = store or JsonStore()
        self._events: dict[str, dict] = {}

    def load_directory(self, directory: str | Path) -> "EventRegistry":
        folder = Path(directory)
        if not folder.exists():
            return self

        for path in sorted(folder.glob("*.json")):
            document = self.store.load(path)
            self.register(document, source=str(path))
        return self

    def register(self, document: dict, source: str = "<memory>") -> None:
        event = require_mapping(document, f"event document {source}")
        event_id = require_string(event, "event_id", source)
        category = require_string(event, "category", source)
        require_string(event, "display_name", source)
        require_int(event, "priority", source, minimum=0)
        require_bool(event, "interrupt", source)
        actions = require_list(event.get("actions"), f"{source}.actions")

        if category not in self.ALLOWED_CATEGORIES:
            raise KnowledgeValidationError(
                f"{source}.category must be one of "
                f"{sorted(self.ALLOWED_CATEGORIES)}"
            )

        for index, action in enumerate(actions):
            action_doc = require_mapping(action, f"{source}.actions[{index}]")
            require_string(action_doc, "type", f"{source}.actions[{index}]")

        if event_id in self._events:
            raise KnowledgeValidationError(f"Duplicate event_id: {event_id}")

        self._events[event_id] = dict(event)

    def get(self, event_id: str) -> dict | None:
        event = self._events.get(event_id)
        return None if event is None else dict(event)

    def all(self) -> tuple[dict, ...]:
        return tuple(dict(item) for item in self._events.values())

    def interrupt_events(self) -> tuple[dict, ...]:
        events = [item for item in self._events.values() if item["interrupt"]]
        events.sort(key=lambda item: item["priority"], reverse=True)
        return tuple(dict(item) for item in events)

    def ids(self) -> tuple[str, ...]:
        return tuple(self._events.keys())

    def __len__(self) -> int:
        return len(self._events)
