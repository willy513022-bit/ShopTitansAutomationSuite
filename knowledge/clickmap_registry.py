from __future__ import annotations

from pathlib import Path

from knowledge.errors import KnowledgeValidationError
from knowledge.json_store import JsonStore
from knowledge.validators import require_list, require_mapping, require_string


class ClickMapRegistry:
    def __init__(self, store: JsonStore | None = None):
        self.store = store or JsonStore()
        self._maps: dict[str, dict] = {}

    def load_file(self, path: str | Path) -> "ClickMapRegistry":
        document = self.store.load(path)
        root = require_mapping(document, str(path))
        resolution = require_string(root, "resolution", str(path))
        points = require_mapping(root.get("points"), f"{path}.points")

        normalized_points = {}
        for action_name, coordinates in points.items():
            values = require_list(coordinates, f"{path}.points.{action_name}")
            if len(values) != 2:
                raise KnowledgeValidationError(
                    f"{path}.points.{action_name} must contain [x, y]"
                )
            x, y = values
            if any(
                isinstance(value, bool) or not isinstance(value, int)
                for value in (x, y)
            ):
                raise KnowledgeValidationError(
                    f"{path}.points.{action_name} coordinates must be integers"
                )
            normalized_points[action_name] = [x, y]

        if resolution in self._maps:
            raise KnowledgeValidationError(
                f"Duplicate clickmap resolution: {resolution}"
            )

        self._maps[resolution] = {
            "resolution": resolution,
            "points": normalized_points,
        }
        return self

    def get_point(self, resolution: str, action_name: str) -> tuple[int, int] | None:
        clickmap = self._maps.get(resolution)
        if clickmap is None:
            return None
        point = clickmap["points"].get(action_name)
        return None if point is None else (point[0], point[1])

    def resolutions(self) -> tuple[str, ...]:
        return tuple(self._maps.keys())

    def __len__(self) -> int:
        return len(self._maps)
