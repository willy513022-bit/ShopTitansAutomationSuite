from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from core.decision_context import DecisionContext

from .evaluation_result import EvaluationResult


class BaseEvaluator(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def evaluate(
        self,
        context: DecisionContext,
        candidate: Any,
    ) -> EvaluationResult:
        raise NotImplementedError
