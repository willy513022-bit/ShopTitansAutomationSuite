from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from core.decision_context import DecisionContext
from core.planner_decision import PlannerDecision
from core.scheduler import Scheduler, SchedulerResult

from .base_planner import BasePlanner


@dataclass(frozen=True, slots=True)
class PlannerFailure:
    planner: str
    error_type: str
    message: str


@dataclass(frozen=True, slots=True)
class PlannerCollection:
    decisions: tuple[PlannerDecision, ...]
    failures: tuple[PlannerFailure, ...] = ()


class PlannerManager:
    """Owns planner registration and gathers independent candidates.

    By default one faulty planner is isolated so the remaining planners can
    still provide safe candidates. Use ``strict=True`` in tests or development
    when exceptions should be raised immediately.
    """

    def __init__(
        self,
        planners: Iterable[BasePlanner] = (),
        *,
        strict: bool = False,
    ) -> None:
        self._planners: list[BasePlanner] = []
        self.strict = strict
        for planner in planners:
            self.register(planner)

    @property
    def planners(self) -> tuple[BasePlanner, ...]:
        return tuple(self._planners)

    def register(self, planner: BasePlanner) -> None:
        key = planner.name.strip().casefold()
        if not key:
            raise ValueError("planner name must not be empty")
        if any(item.name.strip().casefold() == key for item in self._planners):
            raise ValueError(f"planner already registered: {planner.name}")
        self._planners.append(planner)

    def unregister(self, name: str) -> bool:
        key = name.strip().casefold()
        for index, planner in enumerate(self._planners):
            if planner.name.strip().casefold() == key:
                del self._planners[index]
                return True
        return False

    def collect_detailed(self, context: DecisionContext) -> PlannerCollection:
        decisions: list[PlannerDecision] = []
        failures: list[PlannerFailure] = []

        for planner in self._planners:
            try:
                decision = planner.evaluate(context)
            except Exception as exc:
                if self.strict:
                    raise
                failures.append(
                    PlannerFailure(
                        planner=planner.name,
                        error_type=type(exc).__name__,
                        message=str(exc),
                    )
                )
                continue

            if decision is None:
                continue
            if decision.planner.strip().casefold() != planner.name.strip().casefold():
                raise ValueError(
                    f"planner {planner.name!r} returned a decision owned by "
                    f"{decision.planner!r}"
                )
            decisions.append(decision)

        return PlannerCollection(tuple(decisions), tuple(failures))

    def collect(self, context: DecisionContext) -> tuple[PlannerDecision, ...]:
        return self.collect_detailed(context).decisions

    def select(
        self,
        context: DecisionContext,
        scheduler: Scheduler | None = None,
    ) -> SchedulerResult:
        active_scheduler = scheduler or Scheduler()
        return active_scheduler.select_context(self.collect(context), context)
