from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from knowledge.errors import KnowledgeBaseError


class JsonStore:
    def load(self, path: str | Path) -> Any:
        source = Path(path)
        if not source.exists():
            raise KnowledgeBaseError(f"JSON file not found: {source}")

        try:
            with source.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except json.JSONDecodeError as exc:
            raise KnowledgeBaseError(
                f"Invalid JSON in {source}: line {exc.lineno}, column {exc.colno}"
            ) from exc

    def save(self, path: str | Path, data: Any) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
