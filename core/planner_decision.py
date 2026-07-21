from __future__ import annotations
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

@dataclass(frozen=True, slots=True)
class PlannerDecision:
    planner: str
    action: str
    base_priority: float
    reason: str
    confidence: float = 1.0
    payload: Mapping[str, Any] = field(default_factory=dict)
    task_lock: bool = False
    estimated_seconds: float = 0.0
    rule_ids: tuple[str, ...] = ()
    interruptible: bool = True
    retryable: bool = True

    def __post_init__(self):
        if not self.planner.strip(): raise ValueError('planner must not be empty')
        if not self.action.strip(): raise ValueError('action must not be empty')
        if not self.reason.strip(): raise ValueError('reason must not be empty')
        if not 0 <= self.confidence <= 1: raise ValueError('confidence must be between 0 and 1')
        if self.estimated_seconds < 0: raise ValueError('estimated_seconds must not be negative')
        object.__setattr__(self, 'planner', self.planner.strip())
        object.__setattr__(self, 'action', self.action.strip())
        object.__setattr__(self, 'reason', self.reason.strip())
        object.__setattr__(self, 'payload', MappingProxyType(dict(self.payload)))
        object.__setattr__(self, 'rule_ids', tuple(self.rule_ids))

@dataclass(frozen=True, slots=True)
class ScoredDecision:
    decision: PlannerDecision
    final_score: float
    modifiers: Mapping[str, float] = field(default_factory=dict)
    def __post_init__(self):
        object.__setattr__(self, 'modifiers', MappingProxyType(dict(self.modifiers)))
