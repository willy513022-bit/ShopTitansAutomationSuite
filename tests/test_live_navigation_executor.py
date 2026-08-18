from __future__ import annotations

import json

import pytest

from core.planner_decision import PlannerDecision
from knowledge.clickmap_registry import ClickMapRegistry
from navigation import (
    NavigationStateTracker,
    Navigator,
    Screen,
    build_default_screen_graph,
)
from runtime.clickmap_target_resolver import (
    ClickMapTargetResolver,
)
from runtime.craft_execution import (
    CraftExecutionPlanner,
)
from runtime.input_driver import InputDriver
from runtime.live_navigation_executor import (
    LiveNavigationExecutor,
)
from runtime.navigation_target_resolver import (
    NavigationTargetResolver,
)
from runtime.window_manager import (
    WindowBounds,
    WindowManager,
)
from runtime.window_target_resolver import (
    WindowTargetResolver,
)


class RecordingInputDriver(InputDriver):
    """
    Fake InputDriver used by tests.

    It records click requests without touching the real mouse.
    """

    def __init__(self) -> None:
        super().__init__(click_delay=0.0)

        self.clicks: list[
            tuple[int, int]
        ] = []

    def click(
        self,
        x: int,
        y: int,
    ) -> None:
        self.clicks.append(
            (
                int(x),
                int(y),
            )
        )


class FakeWindowManager(WindowManager):
    """
    Deterministic fake Shop Titans window.

    Client origin:
        (-864, 92)

    Client size:
        864 x 1512
    """

    def __init__(self) -> None:
        self.bounds = WindowBounds(
            left=-864,
            top=92,
            width=864,
            height=1512,
        )

    def get_client_bounds(
        self,
    ) -> WindowBounds:
        return self.bounds

    def client_to_screen(
        self,
        x: int,
        y: int,
    ) -> tuple[int, int]:
        return (
            self.bounds.left + int(x),
            self.bounds.top + int(y),
        )


def make_clickmap_registry(
    tmp_path,
) -> ClickMapRegistry:
    path = (
        tmp_path
        / "shop_titans_864x1512.json"
    )

    path.write_text(
        json.dumps(
            {
                "resolution": "864x1512",
                "points": {
                    "craft_button": [
                        799,
                        1310,
                    ],
                },
            }
        ),
        encoding="utf-8",
    )

    return (
        ClickMapRegistry()
        .load_file(path)
    )


def make_plan(
    *,
    start_screen: Screen = Screen.SHOP,
):
    tracker = NavigationStateTracker()

    tracker.update(
        start_screen,
        0.99,
    )

    navigator = Navigator(
        build_default_screen_graph(),
        tracker,
    )

    decision = PlannerDecision(
        planner="blueprint",
        action="CRAFT",
        base_priority=80.0,
        reason="Blueprint test",
        payload={
            "target_item":
                "Bleakspire Roots",
            "requested_count": 1,
        },
    )

    return CraftExecutionPlanner(
        navigator
    ).plan(
        decision
    )


def make_executor(
    tmp_path,
):
    registry = make_clickmap_registry(
        tmp_path
    )

    clickmap_resolver = (
        ClickMapTargetResolver(
            registry,
            "864x1512",
        )
    )

    window_resolver = (
        WindowTargetResolver(
            FakeWindowManager()
        )
    )

    driver = RecordingInputDriver()

    executor = LiveNavigationExecutor(
        navigation_target_resolver=(
            NavigationTargetResolver()
        ),
        clickmap_target_resolver=(
            clickmap_resolver
        ),
        window_target_resolver=(
            window_resolver
        ),
        input_driver=driver,
    )

    return executor, driver


def test_shop_to_craft_clicks_once(
    tmp_path,
):
    executor, driver = make_executor(
        tmp_path
    )

    plan = make_plan()

    result = executor.execute(
        plan
    )

    assert (
        result.navigation_step_count
        == 1
    )

    assert len(driver.clicks) == 1


def test_shop_to_craft_uses_craft_button(
    tmp_path,
):
    executor, _ = make_executor(
        tmp_path
    )

    result = executor.execute(
        make_plan()
    )

    step = result.navigation_steps[0]

    assert (
        step.target_name
        == "craft_button"
    )


def test_client_coordinate_is_preserved(
    tmp_path,
):
    executor, _ = make_executor(
        tmp_path
    )

    result = executor.execute(
        make_plan()
    )

    step = result.navigation_steps[0]

    assert (
        step.client_position
        == (799, 1310)
    )


def test_screen_coordinate_is_resolved(
    tmp_path,
):
    executor, driver = make_executor(
        tmp_path
    )

    result = executor.execute(
        make_plan()
    )

    step = result.navigation_steps[0]

    assert (
        step.screen_position
        == (-65, 1402)
    )

    assert driver.clicks == [
        (-65, 1402)
    ]


def test_non_navigation_steps_do_not_click(
    tmp_path,
):
    executor, driver = make_executor(
        tmp_path
    )

    plan = make_plan(
        start_screen=Screen.CRAFT,
    )

    result = executor.execute(
        plan
    )

    assert (
        result.navigation_step_count
        == 0
    )

    assert driver.clicks == []


def test_result_step_index_matches_plan(
    tmp_path,
):
    executor, _ = make_executor(
        tmp_path
    )

    result = executor.execute(
        make_plan()
    )

    step = result.navigation_steps[0]

    assert step.step_index == 1


def test_rejects_non_plan(
    tmp_path,
):
    executor, _ = make_executor(
        tmp_path
    )

    with pytest.raises(TypeError):
        executor.execute(
            object()
        )


def test_missing_clickmap_target_raises(
    tmp_path,
):
    path = (
        tmp_path
        / "empty_clickmap.json"
    )

    path.write_text(
        json.dumps(
            {
                "resolution": "864x1512",
                "points": {},
            }
        ),
        encoding="utf-8",
    )

    registry = (
        ClickMapRegistry()
        .load_file(path)
    )

    driver = RecordingInputDriver()

    executor = LiveNavigationExecutor(
        navigation_target_resolver=(
            NavigationTargetResolver()
        ),
        clickmap_target_resolver=(
            ClickMapTargetResolver(
                registry,
                "864x1512",
            )
        ),
        window_target_resolver=(
            WindowTargetResolver(
                FakeWindowManager()
            )
        ),
        input_driver=driver,
    )

    with pytest.raises(KeyError):
        executor.execute(
            make_plan()
        )

    assert driver.clicks == []


def test_invalid_navigation_resolver_rejected(
    tmp_path,
):
    registry = make_clickmap_registry(
        tmp_path
    )

    with pytest.raises(TypeError):
        LiveNavigationExecutor(
            navigation_target_resolver=object(),
            clickmap_target_resolver=(
                ClickMapTargetResolver(
                    registry,
                    "864x1512",
                )
            ),
            window_target_resolver=(
                WindowTargetResolver(
                    FakeWindowManager()
                )
            ),
            input_driver=(
                RecordingInputDriver()
            ),
        )


def test_invalid_clickmap_resolver_rejected():
    with pytest.raises(TypeError):
        LiveNavigationExecutor(
            navigation_target_resolver=(
                NavigationTargetResolver()
            ),
            clickmap_target_resolver=object(),
            window_target_resolver=(
                WindowTargetResolver(
                    FakeWindowManager()
                )
            ),
            input_driver=(
                RecordingInputDriver()
            ),
        )


def test_invalid_window_resolver_rejected(
    tmp_path,
):
    registry = make_clickmap_registry(
        tmp_path
    )

    with pytest.raises(TypeError):
        LiveNavigationExecutor(
            navigation_target_resolver=(
                NavigationTargetResolver()
            ),
            clickmap_target_resolver=(
                ClickMapTargetResolver(
                    registry,
                    "864x1512",
                )
            ),
            window_target_resolver=object(),
            input_driver=(
                RecordingInputDriver()
            ),
        )


def test_invalid_input_driver_rejected(
    tmp_path,
):
    registry = make_clickmap_registry(
        tmp_path
    )

    with pytest.raises(TypeError):
        LiveNavigationExecutor(
            navigation_target_resolver=(
                NavigationTargetResolver()
            ),
            clickmap_target_resolver=(
                ClickMapTargetResolver(
                    registry,
                    "864x1512",
                )
            ),
            window_target_resolver=(
                WindowTargetResolver(
                    FakeWindowManager()
                )
            ),
            input_driver=object(),
        )