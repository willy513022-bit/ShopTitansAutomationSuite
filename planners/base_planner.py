from __future__ import annotations

from abc import ABC, abstractmethod

from core.decision_context import DecisionContext
from core.planner_decision import PlannerDecision


class BasePlanner(ABC):
    """Pure decision-candidate producer.

    A planner may inspect only the supplied :class:`DecisionContext` and must
    not perform OCR, mouse/keyboard input, sleeping, or other runtime actions.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Stable planner name used by Strategy and PriorityEngine."""

    @abstractmethod
    def evaluate(self, context: DecisionContext) -> PlannerDecision | None:
        """Return one candidate decision, or ``None`` when no action is safe."""
