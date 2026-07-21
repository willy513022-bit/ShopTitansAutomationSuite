from __future__ import annotations

import ctypes
from dataclasses import dataclass
from typing import Optional

import pygetwindow as gw


@dataclass(frozen=True)
class WindowBounds:
    """視窗客戶區在螢幕上的位置與大小。"""

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
    """尋找 Shop Titans 視窗並處理座標轉換。"""

    def __init__(self, window_title: str = "Shop Titans") -> None:
        self.window_title = window_title
        self._window: Optional[gw.Win32Window] = None

    def find_window(self) -> bool:
        """尋找標題中包含指定文字的可見視窗。"""

        windows = gw.getWindowsWithTitle(self.window_title)

        for window in windows:
            if window.width > 0 and window.height > 0:
                self._window = window
                return True

        self._window = None
        return False

    def require_window(self) -> gw.Win32Window:
        """取得遊戲視窗；找不到時拋出錯誤。"""

        if self._window is None and not self.find_window():
            raise RuntimeError(
                f"找不到視窗：{self.window_title!r}，請確認遊戲已開啟。"
            )

        assert self._window is not None
        return self._window

    def get_client_bounds(self) -> WindowBounds:
        """取得視窗客戶區在螢幕上的實際座標。"""

        window = self.require_window()
        hwnd = window._hWnd

        client_rect = ctypes.wintypes.RECT()

        if not ctypes.windll.user32.GetClientRect(
            hwnd,
            ctypes.byref(client_rect),
        ):
            raise ctypes.WinError()

        client_origin = ctypes.wintypes.POINT(0, 0)

        if not ctypes.windll.user32.ClientToScreen(
            hwnd,
            ctypes.byref(client_origin),
        ):
            raise ctypes.WinError()

        width = client_rect.right - client_rect.left
        height = client_rect.bottom - client_rect.top

        return WindowBounds(
            left=client_origin.x,
            top=client_origin.y,
            width=width,
            height=height,
        )

    def client_to_screen(self, x: int, y: int) -> tuple[int, int]:
        """把遊戲客戶區座標轉換成螢幕座標。"""

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
        把 0.0～1.0 的比例座標轉換成螢幕座標。

        例如：
            (0.5, 0.5) 代表遊戲畫面中心。
        """

        if not 0.0 <= x_ratio <= 1.0:
            raise ValueError("x_ratio 必須介於 0.0 和 1.0 之間。")

        if not 0.0 <= y_ratio <= 1.0:
            raise ValueError("y_ratio 必須介於 0.0 和 1.0 之間。")

        bounds = self.get_client_bounds()

        return (
            bounds.left + round(bounds.width * x_ratio),
            bounds.top + round(bounds.height * y_ratio),
        )

    def activate(self) -> None:
        """將遊戲視窗移到前景。"""

        window = self.require_window()

        if window.isMinimized:
            window.restore()

        window.activate()


if __name__ == "__main__":
    manager = WindowManager()

    if not manager.find_window():
        print("找不到 Shop Titans 視窗。")
        raise SystemExit(1)

    bounds = manager.get_client_bounds()

    print("成功找到 Shop Titans 視窗")
    print(f"客戶區左上角：({bounds.left}, {bounds.top})")
    print(f"客戶區大小：{bounds.width} × {bounds.height}")
    print(f"客戶區中心：{bounds.center}")
    print(
        "比例中心座標：",
        manager.normalized_to_screen(0.5, 0.5),
    )