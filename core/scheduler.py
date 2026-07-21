from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from .decision_context import DecisionContext
from .planner_decision import PlannerDecision, ScoredDecision
from .priority import PriorityEngine
from .strategy import Strategy


@dataclass(frozen=True, slots=True)
class SchedulerResult:
    winner: ScoredDecision | None
    ranked: tuple[ScoredDecision, ...]
    skipped: tuple[PlannerDecision, ...]

    @property
    def has_winner(self) -> bool:
        return self.winner is not None


class Scheduler:
    def __init__(self, priority_engine: PriorityEngine | None = None) -> None:
        self.engine = priority_engine or PriorityEngine()

    def select(
        self,
        decisions: Iterable[PlannerDecision | None],
        strategy: Strategy,
        runtime_modifiers: Mapping[str, float] | None = None,
    ) -> SchedulerResult:
        scored: list[ScoredDecision] = []
        skipped: list[PlannerDecision] = []

        for decision in decisions:
            if decision is None:
                continue
            if not strategy.is_enabled(decision.planner):
                skipped.append(decision)
                continue
            scored.append(
                self.engine.score(
                    decision,
                    strategy,
                    runtime_modifiers,
                )
            )

        ranked = tuple(
            sorted(
                scored,
                key=lambda item: (
                    -item.final_score,
                    -item.decision.confidence,
                    -item.decision.base_priority,
                    item.decision.planner.casefold(),
                    item.decision.action.casefold(),
                ),
            )
        )
        return SchedulerResult(
            winner=ranked[0] if ranked else None,
            ranked=ranked,
            skipped=tuple(skipped),
        )

    def select_context(
        self,
        decisions: Iterable[PlannerDecision | None],
        context: DecisionContext,
    ) -> SchedulerResult:
        """Select using the shared immutable DecisionContext."""

        return self.select(
            decisions=decisions,
            strategy=context.strategy,
            runtime_modifiers=context.runtime_modifiers,
        )
