from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    """One explainable score contribution produced by an evaluator."""

    evaluator: str
    score: float
    reason: str
    rule_ids: tuple[str, ...] = ()
    details: Mapping[str, Any] = field(default_factory=dict)
    eligible: bool = True

    def __post_init__(self) -> None:
        evaluator = self.evaluator.strip()
        reason = self.reason.strip()
        if not evaluator:
            raise ValueError("evaluator must not be empty")
        if not reason:
            raise ValueError("reason must not be empty")
        object.__setattr__(self, "evaluator", evaluator)
        object.__setattr__(self, "reason", reason)
        object.__setattr__(self, "score", float(self.score))
        object.__setattr__(self, "rule_ids", tuple(self.rule_ids))
        object.__setattr__(self, "details", MappingProxyType(dict(self.details)))

    def to_score_factor(self) -> dict[str, Any]:
        return {
            "id": self.evaluator,
            "value": self.score,
            "reason": self.reason,
            "eligible": self.eligible,
            "details": dict(self.details),
        }
