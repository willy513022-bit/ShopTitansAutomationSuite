from __future__ import annotations

from typing import Any

from knowledge.errors import KnowledgeValidationError


def require_mapping(value: Any, label: str) -> dict:
    if not isinstance(value, dict):
        raise KnowledgeValidationError(f"{label} must be an object")
    return value


def require_list(value: Any, label: str) -> list:
    if not isinstance(value, list):
        raise KnowledgeValidationError(f"{label} must be an array")
    return value


def require_string(document: dict, key: str, label: str) -> str:
    value = document.get(key)
    if not isinstance(value, str) or not value.strip():
        raise KnowledgeValidationError(f"{label}.{key} must be a non-empty string")
    return value


def require_bool(document: dict, key: str, label: str) -> bool:
    value = document.get(key)
    if not isinstance(value, bool):
        raise KnowledgeValidationError(f"{label}.{key} must be a boolean")
    return value


def require_int(
    document: dict,
    key: str,
    label: str,
    minimum: int | None = None,
) -> int:
    value = document.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise KnowledgeValidationError(f"{label}.{key} must be an integer")
    if minimum is not None and value < minimum:
        raise KnowledgeValidationError(
            f"{label}.{key} must be at least {minimum}"
        )
    return value
