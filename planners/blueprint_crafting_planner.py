from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from core.decision_context import DecisionContext
from core.planner_decision import PlannerDecision
from planner.blueprint_candidate import BlueprintCandidate
from planner.blueprint_priority import BlueprintPriorityScorer

from .base_planner import BasePlanner


_MISSING = object()


def _read(
    source: Any,
    key: str,
    default: Any = _MISSING,
) -> Any:
    if source is None:
        return default

    if isinstance(source, Mapping):
        return source.get(key, default)

    return getattr(source, key, default)


@dataclass(frozen=True, slots=True)
class BlueprintCraftingPlannerConfig:
    base_priority: float = 55.0
    default_confidence: float = 0.90
    requested_count: int = 1

    def __post_init__(self) -> None:
        if self.requested_count <= 0:
            raise ValueError(
                "requested_count must be greater than 0"
            )

        if not 0.0 <= self.default_confidence <= 1.0:
            raise ValueError(
                "default_confidence must be between 0 and 1"
            )


class BlueprintCraftingPlanner(BasePlanner):
    """
    Select one Blueprint milestone craft target.

    The planner consumes already-resolved BlueprintCandidate objects.

    It intentionally schedules only one craft at a time. Runtime should
    rescan Blueprint progress after execution before scheduling another
    milestone craft.
    """

    def __init__(
        self,
        config: BlueprintCraftingPlannerConfig | None = None,
        *,
        scorer: BlueprintPriorityScorer | None = None,
    ) -> None:
        self.config = (
            config
            or BlueprintCraftingPlannerConfig()
        )

        self.scorer = (
            scorer
            or BlueprintPriorityScorer()
        )

    @property
    def name(self) -> str:
        return "blueprint"

    def evaluate(
        self,
        context: DecisionContext,
    ) -> PlannerDecision | None:
        blueprint = self._blueprint_snapshot(context)

        if blueprint is None:
            return None

        free_slots = self._read_free_slots(
            context,
            blueprint,
        )

        if free_slots is None or free_slots <= 0:
            return None

        candidates = _read(
            blueprint,
            "candidates",
            _MISSING,
        )

        if candidates is _MISSING:
            return None

        normalized = self._normalize_candidates(
            candidates
        )

        if not normalized:
            return None

        craftable = tuple(
            candidate
            for candidate in normalized
            if candidate.remaining > 0
        )

        if not craftable:
            return None

        selected = self.scorer.select_best(
            craftable
        )

        if selected is None:
            return None

        requested_count = min(
            self.config.requested_count,
            selected.remaining,
            free_slots,
        )

        if requested_count <= 0:
            return None

        estimated_stage_seconds = (
            selected.estimated_stage_time_seconds
        )

        payload = {
            "target_item": selected.item_name,
            "requested_count": requested_count,
            "remaining_stage_crafts": selected.remaining,
            "current_progress": (
                selected.state.current_progress
            ),
            "current_target": (
                selected.state.current_target
            ),
            "tier": selected.tier,
            "craft_time_seconds": (
                selected.craft_time_seconds
            ),
            "estimated_stage_time_seconds": (
                estimated_stage_seconds
            ),
            "source": "blueprint_milestone",
            "blueprint_row": selected.state.row,
            "blueprint_column": selected.state.column,
        }

        return PlannerDecision(
            planner=self.name,
            action="CRAFT",
            base_priority=self.config.base_priority,
            reason=(
                f"Selected Blueprint milestone target "
                f"{selected.item_name}: "
                f"{selected.remaining} craft(s) remain; "
                f"estimated current-stage craft time "
                f"is {estimated_stage_seconds} seconds"
            ),
            confidence=self.config.default_confidence,
            payload=payload,
            rule_ids=(
                "BLUEPRINT_MILESTONE_ACTIVE",
                "BLUEPRINT_PRIORITY_SELECTED",
                "PROD_QUEUE_CAPACITY",
            ),
            interruptible=True,
            retryable=True,
        )

    @staticmethod
    def _normalize_candidates(
        candidates: Any,
    ) -> tuple[BlueprintCandidate, ...]:
        if (
            not isinstance(candidates, Iterable)
            or isinstance(
                candidates,
                (
                    str,
                    bytes,
                    Mapping,
                ),
            )
        ):
            return ()

        return tuple(
            candidate
            for candidate in candidates
            if isinstance(
                candidate,
                BlueprintCandidate,
            )
        )

    @staticmethod
    def _blueprint_snapshot(
        context: DecisionContext,
    ) -> Any | None:
        metadata_value = context.metadata.get(
            "blueprint"
        )

        if metadata_value is not None:
            return metadata_value

        return _read(
            context.world_state,
            "blueprint",
            None,
        )

    @staticmethod
    def _read_free_slots(
        context: DecisionContext,
        blueprint: Any,
    ) -> int | None:
        # Allow a Blueprint snapshot to carry the queue fact directly.
        value = _read(
            blueprint,
            "free_slots",
            _MISSING,
        )

        if value is _MISSING:
            production = context.metadata.get(
                "production"
            )

            if production is None:
                production = _read(
                    context.world_state,
                    "production",
                    None,
                )

            value = _read(
                production,
                "free_slots",
                _MISSING,
            )

        if value is _MISSING:
            return None

        try:
            result = int(value)
        except (TypeError, ValueError):
            return None

        if result < 0:
            return None

        return result