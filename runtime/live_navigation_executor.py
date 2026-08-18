from __future__ import annotations

from dataclasses import dataclass

from runtime.clickmap_target_resolver import (
    ClickMapTargetResolver,
)
from runtime.craft_execution import (
    CraftExecutionPlan,
    CraftExecutionStepKind,
)
from runtime.input_driver import InputDriver
from runtime.navigation_target_resolver import (
    NavigationTargetResolver,
)
from runtime.window_target_resolver import (
    WindowTargetResolver,
)


@dataclass(frozen=True, slots=True)
class LiveNavigationStepResult:
    step_index: int
    target_name: str
    client_position: tuple[int, int]
    screen_position: tuple[int, int]


@dataclass(frozen=True, slots=True)
class LiveNavigationResult:
    navigation_steps: tuple[
        LiveNavigationStepResult,
        ...
    ]

    @property
    def navigation_step_count(self) -> int:
        return len(self.navigation_steps)


class LiveNavigationExecutor:
    """
    Execute NAVIGATE steps from a CraftExecutionPlan.

    Pipeline:

        Transition
            -> symbolic navigation target
            -> client-relative ClickTarget
            -> screen-relative ClickTarget
            -> InputDriver.click()

    Non-navigation craft steps are intentionally ignored.

    This executor does not yet verify screen arrival.
    Verification will be added separately.
    """

    def __init__(
        self,
        navigation_target_resolver: NavigationTargetResolver,
        clickmap_target_resolver: ClickMapTargetResolver,
        window_target_resolver: WindowTargetResolver,
        input_driver: InputDriver,
    ) -> None:
        if not isinstance(
            navigation_target_resolver,
            NavigationTargetResolver,
        ):
            raise TypeError(
                "navigation_target_resolver must be "
                "NavigationTargetResolver"
            )

        if not isinstance(
            clickmap_target_resolver,
            ClickMapTargetResolver,
        ):
            raise TypeError(
                "clickmap_target_resolver must be "
                "ClickMapTargetResolver"
            )

        if not isinstance(
            window_target_resolver,
            WindowTargetResolver,
        ):
            raise TypeError(
                "window_target_resolver must be "
                "WindowTargetResolver"
            )

        if not isinstance(
            input_driver,
            InputDriver,
        ):
            raise TypeError(
                "input_driver must be InputDriver"
            )

        self.navigation_target_resolver = (
            navigation_target_resolver
        )
        self.clickmap_target_resolver = (
            clickmap_target_resolver
        )
        self.window_target_resolver = (
            window_target_resolver
        )
        self.input_driver = input_driver

    def execute(
        self,
        plan: CraftExecutionPlan,
    ) -> LiveNavigationResult:
        if not isinstance(
            plan,
            CraftExecutionPlan,
        ):
            raise TypeError(
                "plan must be CraftExecutionPlan"
            )

        results: list[
            LiveNavigationStepResult
        ] = []

        for step_index, step in enumerate(
            plan.steps,
            start=1,
        ):
            if (
                step.kind
                is not CraftExecutionStepKind.NAVIGATE
            ):
                continue

            transition = step.transition

            if transition is None:
                raise ValueError(
                    "NAVIGATE step requires transition"
                )

            navigation_target = (
                self.navigation_target_resolver
                .resolve_transition(
                    transition
                )
            )

            client_target = (
                self.clickmap_target_resolver
                .resolve(
                    navigation_target.target_name
                )
            )

            screen_target = (
                self.window_target_resolver
                .resolve(
                    client_target
                )
            )

            self.input_driver.click(
                *screen_target.position
            )

            results.append(
                LiveNavigationStepResult(
                    step_index=step_index,
                    target_name=(
                        navigation_target.target_name
                    ),
                    client_position=(
                        client_target.position
                    ),
                    screen_position=(
                        screen_target.position
                    ),
                )
            )

        return LiveNavigationResult(
            navigation_steps=tuple(results)
        )