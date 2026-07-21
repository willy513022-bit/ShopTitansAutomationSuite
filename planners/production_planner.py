from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from core.decision_context import DecisionContext
from core.planner_decision import PlannerDecision
from evaluators import EvaluationResult, InventoryEvaluator, QueueEvaluator

from .base_planner import BasePlanner


_MISSING = object()


def _read(source: Any, key: str, default: Any = _MISSING) -> Any:
    if source is None:
        return default
    if isinstance(source, Mapping):
        return source.get(key, default)
    return getattr(source, key, default)


@dataclass(frozen=True, slots=True)
class ProductionPlannerConfig:
    base_priority: float = 40.0
    max_priority: float = 100.0
    default_confidence: float = 0.85


class ProductionPlanner(BasePlanner):
    """Select the best explainable production candidate.

    Preferred normalized snapshot::

        production = {
            "free_slots": 2,
            "candidates": [
                {"item": "Wood Axe", "current_stock": 4, "target_stock": 20},
            ],
        }

    The Sprint 3 ``restock_needed`` / ``target_item`` snapshot remains
    supported for backwards compatibility. Missing required facts never cause
    a guessed action.
    """

    def __init__(
        self,
        config: ProductionPlannerConfig | None = None,
        *,
        evaluators: Iterable[Any] | None = None,
    ) -> None:
        self.config = config or ProductionPlannerConfig()
        self.evaluators = tuple(evaluators or (InventoryEvaluator(), QueueEvaluator()))

    @property
    def name(self) -> str:
        return "craft"

    def evaluate(self, context: DecisionContext) -> PlannerDecision | None:
        production = self._production_snapshot(context)
        if production is None:
            return None

        candidates = _read(production, "candidates", _MISSING)
        if candidates is not _MISSING:
            return self._evaluate_candidates(context, candidates)

        return self._evaluate_legacy_snapshot(production)

    def _evaluate_candidates(
        self,
        context: DecisionContext,
        candidates: Any,
    ) -> PlannerDecision | None:
        if not isinstance(candidates, Iterable) or isinstance(candidates, (str, bytes, Mapping)):
            return None

        ranked: list[tuple[float, str, Any, tuple[EvaluationResult, ...]]] = []
        for candidate in candidates:
            item = _read(candidate, "item", _read(candidate, "name", None))
            if not item:
                continue

            results = tuple(evaluator.evaluate(context, candidate) for evaluator in self.evaluators)
            if not results or any(not result.eligible for result in results):
                continue

            total = self.config.base_priority + sum(result.score for result in results)
            ranked.append((total, str(item), candidate, results))

        if not ranked:
            return None

        # Deterministic tie-break by item name.
        ranked.sort(key=lambda row: (-row[0], row[1].casefold()))
        total, item, candidate, results = ranked[0]
        score = min(self.config.max_priority, total)
        rule_ids = tuple(rule_id for result in results for rule_id in result.rule_ids)
        factors = tuple(result.to_score_factor() for result in results)
        explanation = "; ".join(result.reason for result in results)

        payload = {
            "target_item": item,
            "candidate": dict(candidate) if isinstance(candidate, Mapping) else candidate,
            "evaluation_results": factors,
            "score_factors": factors,
        }
        return PlannerDecision(
            planner=self.name,
            action="CRAFT",
            base_priority=score,
            reason=f"Selected {item}: {explanation}",
            confidence=self.config.default_confidence,
            payload=payload,
            rule_ids=rule_ids,
            interruptible=True,
            retryable=True,
        )

    def _evaluate_legacy_snapshot(self, production: Any) -> PlannerDecision | None:
        free_slots_raw = _read(production, "free_slots")
        restock_raw = _read(production, "restock_needed")
        if free_slots_raw is _MISSING or restock_raw is _MISSING:
            return None

        try:
            free_slots = int(free_slots_raw)
        except (TypeError, ValueError):
            return None
        if free_slots <= 0 or not bool(restock_raw):
            return None

        target_item = _read(production, "target_item", None)
        queue_score = min(20.0, free_slots * 5.0)
        restock_score = 20.0
        score = min(self.config.max_priority, self.config.base_priority + queue_score + restock_score)
        factors = (
            {"id": "PROD_QUEUE_CAPACITY", "value": queue_score, "reason": f"{free_slots} free slot(s)"},
            {"id": "PROD_RESTOCK", "value": restock_score, "reason": "Restocking is required"},
        )
        payload: dict[str, Any] = {
            "free_slots": free_slots,
            "score_factors": factors,
            "evaluation_results": factors,
        }
        if target_item:
            payload["target_item"] = str(target_item)

        target_text = f" for {target_item}" if target_item else ""
        return PlannerDecision(
            planner=self.name,
            action="CRAFT",
            base_priority=score,
            reason=f"Production has {free_slots} free slot(s) and requires restocking{target_text}",
            confidence=self.config.default_confidence,
            payload=payload,
            rule_ids=("PROD_FREE_SLOT", "PROD_RESTOCK"),
            interruptible=True,
            retryable=True,
        )

    @staticmethod
    def _production_snapshot(context: DecisionContext) -> Any | None:
        metadata_value = context.metadata.get("production")
        if metadata_value is not None:
            return metadata_value
        return _read(context.world_state, "production", None)
