from __future__ import annotations

import pytest

from runtime.click_target import ClickTarget
from runtime.window_manager import (
    WindowBounds,
    WindowManager,
)
from runtime.window_target_resolver import (
    WindowTargetResolver,
)


class FakeWindowManager(
    WindowManager
):
    def __init__(
        self,
        *,
        left=100,
        top=200,
        width=878,
        height=1550,
    ):
        self.bounds = WindowBounds(
            left=left,
            top=top,
            width=width,
            height=height,
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
            self.bounds.left + x,
            self.bounds.top + y,
        )


def test_converts_client_relative_to_screen():
    resolver = WindowTargetResolver(
        FakeWindowManager(
            left=100,
            top=200,
        )
    )

    target = resolver.resolve(
        ClickTarget(
            x=700,
            y=1400,
            name="production_button",
            confidence=1.0,
            source="clickmap:878x1550",
        )
    )

    assert target.position == (
        800,
        1600,
    )

    assert (
        target.name
        == "production_button"
    )

    assert (
        target.source
        == "window:clickmap:878x1550"
    )


def test_preserves_confidence():
    resolver = WindowTargetResolver(
        FakeWindowManager()
    )

    target = resolver.resolve(
        ClickTarget(
            x=100,
            y=100,
            confidence=0.91,
        )
    )

    assert target.confidence == 0.91


def test_origin_coordinate_is_valid():
    resolver = WindowTargetResolver(
        FakeWindowManager(
            left=-800,
            top=50,
        )
    )

    target = resolver.resolve(
        ClickTarget(
            x=0,
            y=0,
        )
    )

    assert target.position == (
        -800,
        50,
    )


def test_negative_relative_x_rejected():
    resolver = WindowTargetResolver(
        FakeWindowManager()
    )

    with pytest.raises(ValueError):
        resolver.resolve(
            ClickTarget(
                x=-1,
                y=100,
            )
        )


def test_negative_relative_y_rejected():
    resolver = WindowTargetResolver(
        FakeWindowManager()
    )

    with pytest.raises(ValueError):
        resolver.resolve(
            ClickTarget(
                x=100,
                y=-1,
            )
        )


def test_x_outside_client_rejected():
    resolver = WindowTargetResolver(
        FakeWindowManager(
            width=878,
        )
    )

    with pytest.raises(ValueError):
        resolver.resolve(
            ClickTarget(
                x=878,
                y=100,
            )
        )


def test_y_outside_client_rejected():
    resolver = WindowTargetResolver(
        FakeWindowManager(
            height=1550,
        )
    )

    with pytest.raises(ValueError):
        resolver.resolve(
            ClickTarget(
                x=100,
                y=1550,
            )
        )


def test_invalid_target_rejected():
    resolver = WindowTargetResolver(
        FakeWindowManager()
    )

    with pytest.raises(TypeError):
        resolver.resolve(
            object()
        )


def test_invalid_window_manager_rejected():
    with pytest.raises(TypeError):
        WindowTargetResolver(
            object()
        )