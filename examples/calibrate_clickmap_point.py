from __future__ import annotations

import ctypes
import ctypes.wintypes

from runtime.window_manager import WindowManager


def get_cursor_position() -> tuple[int, int]:
    point = ctypes.wintypes.POINT()

    success = ctypes.windll.user32.GetCursorPos(
        ctypes.byref(point)
    )

    if not success:
        raise OSError("GetCursorPos failed")

    return point.x, point.y


def main() -> None:
    manager = WindowManager("Shop Titans")

    if not manager.find_window():
        raise RuntimeError(
            "Unable to find Shop Titans window"
        )

    bounds = manager.get_client_bounds()

    print()
    print("=== Shop Titans ClickMap Calibration ===")
    print()
    print(
        f"Client origin : "
        f"({bounds.left}, {bounds.top})"
    )
    print(
        f"Client size   : "
        f"{bounds.width}x{bounds.height}"
    )
    print()
    print(
        "Move the mouse onto the CENTER of the "
        "button you want to calibrate."
    )
    print(
        "Do not click the game."
    )
    print()
    input(
        "When the mouse is in position, "
        "press ENTER here..."
    )

    screen_x, screen_y = get_cursor_position()

    client_x = screen_x - bounds.left
    client_y = screen_y - bounds.top

    print()
    print("=== Result ===")
    print(
        f"Screen position : "
        f"({screen_x}, {screen_y})"
    )
    print(
        f"Client position : "
        f"({client_x}, {client_y})"
    )

    inside = (
        0 <= client_x < bounds.width
        and
        0 <= client_y < bounds.height
    )

    print(
        f"Inside client   : {inside}"
    )

    if not inside:
        print()
        print(
            "WARNING: Cursor was outside "
            "the Shop Titans client area."
        )
        return

    print()
    print("ClickMap JSON:")
    print(
        f'    "target_name": '
        f'[{client_x}, {client_y}]'
    )


if __name__ == "__main__":
    main()