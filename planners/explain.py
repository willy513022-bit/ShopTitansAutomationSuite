from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

from core.planner_decision import ScoredDecision


@dataclass(frozen=True, slots=True)
class ExplainFactor:
    name: str
    value: float
    source: str


@dataclass(frozen=True, slots=True)
class DecisionTrace:
    planner: str
    action: str
    reason: str
    base_priority: float
    final_score: float
    confidence: float
    factors: tuple[ExplainFactor, ...]
    rule_ids: tuple[str, ...]
    created_at: datetime

    @classmethod
    def from_scored_decision(
        cls,
        scored: ScoredDecision,
        *,
        created_at: datetime | None = None,
    ) -> "DecisionTrace":
        decision = scored.decision
        factors: list[ExplainFactor] = []

        raw_factors = decision.payload.get("score_factors", ())
        if isinstance(raw_factors, (tuple, list)):
            for item in raw_factors:
                if not isinstance(item, Mapping):
                    continue
                name = str(item.get("id", "planner_factor"))
                try:
                    value = float(item.get("value", 0.0))
                except (TypeError, ValueError):
                    continue
                factors.append(ExplainFactor(name, value, "planner"))

        for name, value in scored.modifiers.items():
            factors.append(ExplainFactor(str(name), float(value), "priority_engine"))

        return cls(
            planner=decision.planner,
            action=decision.action,
            reason=decision.reason,
            base_priority=decision.base_priority,
            final_score=scored.final_score,
            confidence=decision.confidence,
            factors=tuple(factors),
            rule_ids=decision.rule_ids,
            created_at=created_at or datetime.now(timezone.utc),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "planner": self.planner,
            "action": self.action,
            "reason": self.reason,
            "base_priority": self.base_priority,
            "final_score": self.final_score,
            "confidence": self.confidence,
            "factors": [
                {"name": factor.name, "value": factor.value, "source": factor.source}
                for factor in self.factors
            ],
            "rule_ids": list(self.rule_ids),
            "created_at": self.created_at.isoformat(),
        }
