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
class QueueEvaluatorConfig:
    points_per_free_slot: float = 5.0
    max_score: float = 20.0


class QueueEvaluator(BaseEvaluator):
    def __init__(self, config: QueueEvaluatorConfig | None = None) -> None:
        self.config = config or QueueEvaluatorConfig()

    @property
    def name(self) -> str:
        return "PROD_QUEUE_CAPACITY"

    def evaluate(self, context: DecisionContext, candidate: Any) -> EvaluationResult:
        production = context.metadata.get("production")
        if production is None:
            world_state = context.world_state
            if isinstance(world_state, Mapping):
                production = world_state.get("production")
            else:
                production = getattr(world_state, "production", None)

        free_slots = _read(production, "free_slots")
        try:
            free_slots_value = int(free_slots)
        except (TypeError, ValueError):
            return EvaluationResult(
                evaluator=self.name,
                score=0,
                reason="Production queue capacity is unknown",
                rule_ids=("PROD_QUEUE_UNKNOWN",),
                eligible=False,
            )

        score = min(
            self.config.max_score,
            max(0, free_slots_value) * self.config.points_per_free_slot,
        )
        return EvaluationResult(
            evaluator=self.name,
            score=score,
            reason=(
                f"Production queue has {free_slots_value} free slot(s)"
                if free_slots_value > 0
                else "Production queue is full"
            ),
            rule_ids=("PROD_QUEUE_CAPACITY",),
            details={"free_slots": free_slots_value},
            eligible=free_slots_value > 0,
        )
