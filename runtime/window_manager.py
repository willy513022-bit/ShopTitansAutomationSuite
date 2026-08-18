from __future__ import annotations

import ctypes
import ctypes.wintypes
from dataclasses import dataclass
from typing import Optional

import pygetwindow as gw


@dataclass(frozen=True)
class WindowBounds:
    """
    Windows client-area bounds in screen coordinates.
    """

    left: int
    top: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.left + self.width

    @property
    def bottom(self) -> int:
        return self.top + self.height

    @property
    def center(self) -> tuple[int, int]:
        return (
            self.left + self.width // 2,
            self.top + self.height // 2,
        )


class WindowManager:
    """
    Locate and manage the Shop Titans game window.

    pygetwindow.getWindowsWithTitle() performs substring matching,
    so another window such as CMD may accidentally contain
    "Shop Titans" in its title.

    Window selection therefore prefers:
    1. valid, non-minimized windows
    2. exact title matches
    3. largest candidate as fallback
    """

    def __init__(
        self,
        window_title: str = "Shop Titans",
    ) -> None:
        self.window_title = window_title
        self._window: Optional[
            gw.Win32Window
        ] = None

    def find_window(self) -> bool:
        title = self.window_title.strip()

        if not title:
            self._window = None
            return False

        windows = gw.getWindowsWithTitle(
            title
        )

        candidates = [
            window
            for window in windows
            if (
                window.width > 0
                and window.height > 0
                and not window.isMinimized
            )
        ]

        if not candidates:
            self._window = None
            return False

        exact_matches = [
            window
            for window in candidates
            if (
                window.title.strip().casefold()
                == title.casefold()
            )
        ]

        pool = (
            exact_matches
            if exact_matches
            else candidates
        )

        self._window = max(
            pool,
            key=lambda window: (
                window.width
                * window.height
            ),
        )

        return True

    def require_window(
        self,
    ) -> gw.Win32Window:
        if (
            self._window is None
            and not self.find_window()
        ):
            raise RuntimeError(
                "Unable to find window: "
                f"{self.window_title!r}"
            )

        assert self._window is not None

        return self._window

    def get_client_bounds(
        self,
    ) -> WindowBounds:
        """
        Return the client area in Windows screen coordinates.
        """

        window = self.require_window()
        hwnd = window._hWnd

        client_rect = (
            ctypes.wintypes.RECT()
        )

        if not ctypes.windll.user32.GetClientRect(
            hwnd,
            ctypes.byref(client_rect),
        ):
            raise ctypes.WinError()

        client_origin = (
            ctypes.wintypes.POINT(
                0,
                0,
            )
        )

        if not ctypes.windll.user32.ClientToScreen(
            hwnd,
            ctypes.byref(client_origin),
        ):
            raise ctypes.WinError()

        width = (
            client_rect.right
            - client_rect.left
        )

        height = (
            client_rect.bottom
            - client_rect.top
        )

        return WindowBounds(
            left=client_origin.x,
            top=client_origin.y,
            width=width,
            height=height,
        )

    def client_to_screen(
        self,
        x: int,
        y: int,
    ) -> tuple[int, int]:
        """
        Convert client-relative coordinates to Windows
        screen-absolute coordinates.
        """

        bounds = self.get_client_bounds()

        return (
            bounds.left + int(x),
            bounds.top + int(y),
        )

    def normalized_to_screen(
        self,
        x_ratio: float,
        y_ratio: float,
    ) -> tuple[int, int]:
        """
        Convert normalized client coordinates (0.0 - 1.0)
        to Windows screen coordinates.
        """

        if not 0.0 <= x_ratio <= 1.0:
            raise ValueError(
                "x_ratio must be between "
                "0.0 and 1.0"
            )

        if not 0.0 <= y_ratio <= 1.0:
            raise ValueError(
                "y_ratio must be between "
                "0.0 and 1.0"
            )

        bounds = self.get_client_bounds()

        return (
            bounds.left
            + round(
                bounds.width * x_ratio
            ),
            bounds.top
            + round(
                bounds.height * y_ratio
            ),
        )

    def activate(self) -> None:
        window = self.require_window()

        if window.isMinimized:
            window.restore()

        window.activate()


if __name__ == "__main__":
    manager = WindowManager()

    if not manager.find_window():
        print(
            "Unable to find Shop Titans window."
        )
        raise SystemExit(1)

    window = manager.require_window()
    bounds = manager.get_client_bounds()

    print("Shop Titans window found")
    print(
        f"Title        : {window.title!r}"
    )
    print(
        f"Client origin: "
        f"({bounds.left}, {bounds.top})"
    )
    print(
        f"Client size  : "
        f"{bounds.width}x{bounds.height}"
    )
    print(
        f"Client center: "
        f"{bounds.center}"
    )