from unittest.mock import MagicMock, patch

from runtime.window_manager import WindowManager


def make_window(
    title: str,
    width: int,
    height: int,
    *,
    minimized: bool = False,
):
    window = MagicMock()

    window.title = title
    window.width = width
    window.height = height
    window.isMinimized = minimized

    return window


def test_exact_title_is_preferred():
    cmd = make_window(
        'cmd.exe - python "Shop Titans"',
        1000,
        700,
    )

    game = make_window(
        "Shop Titans",
        878,
        1550,
    )

    with patch(
        "runtime.window_manager.gw.getWindowsWithTitle",
        return_value=[cmd, game],
    ):
        manager = WindowManager(
            "Shop Titans"
        )

        assert manager.find_window()

        assert (
            manager.require_window()
            is game
        )


def test_exact_title_beats_larger_partial_match():
    partial = make_window(
        "Shop Titans Debug Window",
        2000,
        2000,
    )

    game = make_window(
        "Shop Titans",
        878,
        1550,
    )

    with patch(
        "runtime.window_manager.gw.getWindowsWithTitle",
        return_value=[partial, game],
    ):
        manager = WindowManager(
            "Shop Titans"
        )

        assert manager.find_window()

        assert (
            manager.require_window()
            is game
        )


def test_largest_partial_match_is_fallback():
    small = make_window(
        "Shop Titans Helper",
        500,
        300,
    )

    large = make_window(
        "Shop Titans Launcher",
        900,
        700,
    )

    with patch(
        "runtime.window_manager.gw.getWindowsWithTitle",
        return_value=[small, large],
    ):
        manager = WindowManager(
            "Shop Titans"
        )

        assert manager.find_window()

        assert (
            manager.require_window()
            is large
        )


def test_minimized_window_is_ignored():
    minimized = make_window(
        "Shop Titans",
        878,
        1550,
        minimized=True,
    )

    valid = make_window(
        "Shop Titans Helper",
        800,
        1200,
    )

    with patch(
        "runtime.window_manager.gw.getWindowsWithTitle",
        return_value=[minimized, valid],
    ):
        manager = WindowManager(
            "Shop Titans"
        )

        assert manager.find_window()

        assert (
            manager.require_window()
            is valid
        )


def test_returns_false_when_no_valid_window():
    invalid = make_window(
        "Shop Titans",
        0,
        0,
    )

    with patch(
        "runtime.window_manager.gw.getWindowsWithTitle",
        return_value=[invalid],
    ):
        manager = WindowManager(
            "Shop Titans"
        )

        assert not manager.find_window()


def test_empty_title_returns_false():
    manager = WindowManager("   ")

    assert not manager.find_window()