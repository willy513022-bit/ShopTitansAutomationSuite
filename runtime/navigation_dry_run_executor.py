from __future__ import annotations

from dataclasses import dataclass

from runtime.craft_execution import (
    CraftExecutionPlan,
    CraftExecutionStep,
    CraftExecutionStepKind,
)
from runtime.navigation_target_resolver import (
    NavigationTargetResolver,
)


@dataclass(frozen=True, slots=True)
class NavigationDryRunStepResult:
    step_index: int
    target_name: str
    description: str
    executed: bool = False


@dataclass(frozen=True, slots=True)
class NavigationDryRunResult:
    plan: CraftExecutionPlan
    navigation_steps: tuple[
        NavigationDryRunStepResult,
        ...
    ]

    @property
    def navigation_step_count(self) -> int:
        return len(self.navigation_steps)


class NavigationDryRunExecutor:
    """
    Resolve NAVIGATE CraftExecutionSteps into symbolic runtime targets.

    No mouse input is performed.

    Example:

        SHOP -> PRODUCTION
        OPEN_PRODUCTION
            ->
        production_button
    """

    def __init__(
        self,
        resolver: NavigationTargetResolver
        | None = None,
    ) -> None:
        self.resolver = (
            resolver
            or NavigationTargetResolver()
        )

    def execute(
        self,
        plan: CraftExecutionPlan,
    ) -> NavigationDryRunResult:
        if not isinstance(
            plan,
            CraftExecutionPlan,
        ):
            raise TypeError(
                "plan must be CraftExecutionPlan"
            )

        results: list[
            NavigationDryRunStepResult
        ] = []

        for index, step in enumerate(
            plan.steps,
            start=1,
        ):
            if (
                step.kind
                is not CraftExecutionStepKind.NAVIGATE
            ):
                continue

            results.append(
                self.resolve_step(
                    step,
                    step_index=index,
                )
            )

        return NavigationDryRunResult(
            plan=plan,
            navigation_steps=tuple(results),
        )

    def resolve_step(
        self,
        step: CraftExecutionStep,
        *,
        step_index: int,
    ) -> NavigationDryRunStepResult:
        if not isinstance(
            step,
            CraftExecutionStep,
        ):
            raise TypeError(
                "step must be CraftExecutionStep"
            )

        if (
            step.kind
            is not CraftExecutionStepKind.NAVIGATE
        ):
            raise ValueError(
                "step must be NAVIGATE"
            )

        if step.transition is None:
            raise ValueError(
                "NAVIGATE step missing transition"
            )

        navigation_target = (
            self.resolver.resolve_transition(
                step.transition
            )
        )

        return NavigationDryRunStepResult(
            step_index=step_index,
            target_name=(
                navigation_target.target_name
            ),
            description=(
                f"Dry Run: would execute "
                f"{step.transition.action.value} "
                f"by targeting "
                f"{navigation_target.target_name}"
            ),
            executed=False,
        )