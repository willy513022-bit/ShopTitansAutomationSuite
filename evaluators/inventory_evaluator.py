from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from core.decision_context import DecisionContext

from .base_evaluator import BaseEvaluator
from .evaluation_result import EvaluationResult


def _read(source: Any, key: str, default: Any = None) -> Any:
    if source is None:
        return default
    if isinstance(source, Mapping):
        return source.get(key, default)
    return getattr(source, key, default)


@dataclass(frozen=True, slots=True)
class InventoryEvaluatorConfig:
    points_per_missing_item: float = 2.0
    max_score: float = 40.0


class InventoryEvaluator(BaseEvaluator):
    def __init__(self, config: InventoryEvaluatorConfig | None = None) -> None:
        self.config = config or InventoryEvaluatorConfig()

    @property
    def name(self) -> str:
        return "PROD_INVENTORY_GAP"

    def evaluate(self, context: DecisionContext, candidate: Any) -> EvaluationResult:
        current = _read(candidate, "current_stock")
        target = _read(candidate, "target_stock")
        item = str(_read(candidate, "item", _read(candidate, "name", "item")))

        try:
            current_value = max(0, int(current))
            target_value = max(0, int(target))
        except (TypeError, ValueError):
            return EvaluationResult(
                evaluator=self.name,
                score=0,
                reason=f"Inventory facts are unavailable for {item}",
                rule_ids=("PROD_INVENTORY_UNKNOWN",),
                details={"item": item},
                eligible=False,
            )

        missing = max(0, target_value - current_value)
        score = min(self.config.max_score, missing * self.config.points_per_missing_item)
        return EvaluationResult(
            evaluator=self.name,
            score=score,
            reason=(
                f"{item} is missing {missing} unit(s) from target"
                if missing
                else f"{item} already meets its inventory target"
            ),
            rule_ids=("PROD_INVENTORY_GAP",),
            details={
                "item": item,
                "current_stock": current_value,
                "target_stock": target_value,
                "missing": missing,
            },
            eligible=missing > 0,
        )
