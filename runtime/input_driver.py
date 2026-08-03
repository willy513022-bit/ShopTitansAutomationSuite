from __future__ import annotations

import ctypes
import time

# Windows MouseEvent Flags
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010


class InputDriver:
    """
    Runtime 的滑鼠輸入驅動。

    全專案統一使用 Windows API，
    避免 pyautogui 在 DPI 縮放下造成座標偏移。
    """

    def __init__(self, click_delay: float = 0.05):
        self.click_delay = click_delay

    def move_to(
        self,
        x: int,
        y: int,
    ) -> None:
        success = ctypes.windll.user32.SetCursorPos(
            int(x),
            int(y),
        )

        if not success:
            raise OSError("SetCursorPos failed")

    def click(
        self,
        x: int,
        y: int,
    ) -> None:

        self.move_to(x, y)

        user32 = ctypes.windll.user32

        user32.mouse_event(
            MOUSEEVENTF_LEFTDOWN,
            0,
            0,
            0,
            0,
        )

        time.sleep(0.03)

        user32.mouse_event(
            MOUSEEVENTF_LEFTUP,
            0,
            0,
            0,
            0,
        )

        time.sleep(self.click_delay)

    def double_click(
        self,
        x: int,
        y: int,
    ) -> None:

        self.click(x, y)
        time.sleep(0.05)
        self.click(x, y)

    def right_click(
        self,
        x: int,
        y: int,
    ) -> None:

        self.move_to(x, y)

        user32 = ctypes.windll.user32

        user32.mouse_event(
            MOUSEEVENTF_RIGHTDOWN,
            0,
            0,
            0,
            0,
        )

        time.sleep(0.03)

        user32.mouse_event(
            MOUSEEVENTF_RIGHTUP,
            0,
            0,
            0,
            0,
        )

        time.sleep(self.click_delay)

    def drag(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: float = 0.25,
    ) -> None:

        user32 = ctypes.windll.user32

        self.move_to(start_x, start_y)

        user32.mouse_event(
            MOUSEEVENTF_LEFTDOWN,
            0,
            0,
            0,
            0,
        )

        steps = max(1, int(duration * 120))

        for i in range(steps):
            t = (i + 1) / steps

            x = round(start_x + (end_x - start_x) * t)
            y = round(start_y + (end_y - start_y) * t)

            self.move_to(x, y)

            time.sleep(duration / steps)

        user32.mouse_event(
            MOUSEEVENTF_LEFTUP,
            0,
            0,
            0,
            0,
        )

    def scroll(
        self,
        amount: int,
    ) -> None:
        ctypes.windll.user32.mouse_event(
            0x0800,
            0,
            0,
            int(amount),
            0,
        )


if __name__ == "__main__":
    print("InputDriver Loaded")