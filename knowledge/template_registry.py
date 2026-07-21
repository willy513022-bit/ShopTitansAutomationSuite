from __future__ import annotations

from pathlib import Path

from knowledge.errors import KnowledgeValidationError
from knowledge.json_store import JsonStore
from knowledge.validators import (
    require_list,
    require_mapping,
    require_string,
)


class TemplateRegistry:
    def __init__(self, store: JsonStore | None = None):
        self.store = store or JsonStore()
        self._templates: dict[str, dict] = {}

    def load_file(self, path: str | Path) -> "TemplateRegistry":
        document = self.store.load(path)
        root = require_mapping(document, str(path))
        templates = require_list(root.get("templates"), f"{path}.templates")

        for index, template in enumerate(templates):
            self.register(template, source=f"{path}.templates[{index}]")
        return self

    def register(self, document: dict, source: str = "<memory>") -> None:
        template = require_mapping(document, source)
        template_id = require_string(template, "template_id", source)
        require_string(template, "screen_state", source)
        require_string(template, "relative_path", source)

        threshold = template.get("threshold", 0.85)
        if not isinstance(threshold, (int, float)) or isinstance(threshold, bool):
            raise KnowledgeValidationError(f"{source}.threshold must be numeric")
        if not 0.0 <= float(threshold) <= 1.0:
            raise KnowledgeValidationError(
                f"{source}.threshold must be between 0 and 1"
            )

        if template_id in self._templates:
            raise KnowledgeValidationError(
                f"Duplicate template_id: {template_id}"
            )

        normalized = dict(template)
        normalized["threshold"] = float(threshold)
        self._templates[template_id] = normalized

    def get(self, template_id: str) -> dict | None:
        template = self._templates.get(template_id)
        return None if template is None else dict(template)

    def for_state(self, screen_state: str) -> tuple[dict, ...]:
        return tuple(
            dict(item)
            for item in self._templates.values()
            if item["screen_state"] == screen_state
        )

    def resolve_path(self, template_id: str, base_directory: str | Path) -> Path:
        template = self._templates.get(template_id)
        if template is None:
            raise KeyError(template_id)
        return Path(base_directory) / template["relative_path"]

    def __len__(self) -> int:
        return len(self._templates)
