from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from core.planner_decision import PlannerDecision
from navigation import Navigator, Screen
from navigation.navigator import NavigationPlan


class CraftExecutionStepKind(str, Enum):
    NAVIGATE = "NAVIGATE"
    FIND_ITEM = "FIND_ITEM"
    SELECT_ITEM = "SELECT_ITEM"
    START_CRAFT = "START_CRAFT"
    VERIFY_CRAFT_STARTED = "VERIFY_CRAFT_STARTED"


@dataclass(frozen=True, slots=True)
class CraftExecutionStep:
    kind: CraftExecutionStepKind
    description: str
    target_item: str | None = None


@dataclass(frozen=True, slots=True)
class CraftExecutionPlan:
    target_item: str
    requested_count: int
    navigation: NavigationPlan
    steps: tuple[CraftExecutionStep, ...]

    @property
    def requires_navigation(self) -> bool:
        return not self.navigation.is_noop

    @property
    def total_steps(self) -> int:
        return len(self.steps)


class CraftExecutionPlanner:
    """
    Convert a PlannerDecision(action='CRAFT') into a deterministic
    runtime execution plan.

    This class does not perform any mouse input.

    Planner layer decides WHAT should be crafted.
    CraftExecutionPlanner decides HOW runtime should attempt it.
    """

    def __init__(
        self,
        navigator: Navigator,
    ) -> None:
        if not isinstance(navigator, Navigator):
            raise TypeError(
                "navigator must be Navigator"
            )

        self.navigator = navigator

    def plan(
        self,
        decision: PlannerDecision,
    ) -> CraftExecutionPlan:
        if not isinstance(
            decision,
            PlannerDecision,
        ):
            raise TypeError(
                "decision must be PlannerDecision"
            )

        if decision.action.upper() != "CRAFT":
            raise ValueError(
                "decision action must be CRAFT"
            )

        target_item_raw = decision.payload.get(
            "target_item"
        )

        if target_item_raw is None:
            raise ValueError(
                "CRAFT decision requires "
                "payload['target_item']"
            )

        target_item = str(
            target_item_raw
        ).strip()

        if not target_item:
            raise ValueError(
                "target_item cannot be empty"
            )

        requested_count_raw = (
            decision.payload.get(
                "requested_count",
                1,
            )
        )

        try:
            requested_count = int(
                requested_count_raw
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "requested_count must be an integer"
            ) from exc

        if requested_count <= 0:
            raise ValueError(
                "requested_count must be positive"
            )

        navigation = self.navigator.plan(
            Screen.CRAFT
        )

        steps: list[
            CraftExecutionStep
        ] = []

        for transition in navigation.transitions:
            steps.append(
                CraftExecutionStep(
                    kind=CraftExecutionStepKind.NAVIGATE,
                    description=(
                        f"{transition.source.value} "
                        f"-> {transition.target.value} "
                        f"via {transition.action.value}"
                    ),
                )
            )

        steps.extend(
            (
                CraftExecutionStep(
                    kind=CraftExecutionStepKind.FIND_ITEM,
                    description=(
                        f"Locate blueprint for "
                        f"{target_item}"
                    ),
                    target_item=target_item,
                ),
                CraftExecutionStep(
                    kind=CraftExecutionStepKind.SELECT_ITEM,
                    description=(
                        f"Select {target_item}"
                    ),
                    target_item=target_item,
                ),
                CraftExecutionStep(
                    kind=CraftExecutionStepKind.START_CRAFT,
                    description=(
                        f"Start crafting "
                        f"{target_item} "
                        f"x{requested_count}"
                    ),
                    target_item=target_item,
                ),
                CraftExecutionStep(
                    kind=(
                        CraftExecutionStepKind
                        .VERIFY_CRAFT_STARTED
                    ),
                    description=(
                        f"Verify that crafting "
                        f"started for {target_item}"
                    ),
                    target_item=target_item,
                ),
            )
        )

        return CraftExecutionPlan(
            target_item=target_item,
            requested_count=requested_count,
            navigation=navigation,
            steps=tuple(steps),
        )