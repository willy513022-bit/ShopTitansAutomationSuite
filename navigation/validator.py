from __future__ import annotations

from dataclasses import dataclass

from .screen import Screen
from .transition import Transition


@dataclass(frozen=True)
class ValidationResult:
    success: bool
    expected: Screen
    observed: Screen
    confidence: float
    reason: str


class NavigationValidator:
    def validate_arrival(
        self,
        expected: Screen,
        observed: Screen,
        confidence: float,
        *,
        minimum_confidence: float = 0.80,
    ) -> ValidationResult:
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")

        if confidence < minimum_confidence:
            return ValidationResult(
                success=False,
                expected=expected,
                observed=observed,
                confidence=confidence,
                reason="LOW_CONFIDENCE",
            )

        if observed != expected:
            return ValidationResult(
                success=False,
                expected=expected,
                observed=observed,
                confidence=confidence,
                reason="WRONG_SCREEN",
            )

        return ValidationResult(
            success=True,
            expected=expected,
            observed=observed,
            confidence=confidence,
            reason="ARRIVED",
        )

    def validate_transition(
        self,
        transition: Transition,
        observed: Screen,
        confidence: float,
        *,
        minimum_confidence: float = 0.80,
    ) -> ValidationResult:
        return self.validate_arrival(
            expected=transition.target,
            observed=observed,
            confidence=confidence,
            minimum_confidence=minimum_confidence,
        )
