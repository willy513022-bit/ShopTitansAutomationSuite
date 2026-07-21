from __future__ import annotations

import time

import pyautogui


class InputDriver:
    """統一管理所有滑鼠、鍵盤輸入。"""

    def __init__(self, click_delay: float = 0.05):
        self.click_delay = click_delay

    def move_to(self, x: int, y: int, duration: float = 0.0) -> None:
        pyautogui.moveTo(x, y, duration=duration)

    def click(self, x: int, y: int) -> None:
        pyautogui.click(x, y)
        time.sleep(self.click_delay)

    def double_click(self, x: int, y: int) -> None:
        pyautogui.doubleClick(x, y)
        time.sleep(self.click_delay)

    def right_click(self, x: int, y: int) -> None:
        pyautogui.rightClick(x, y)
        time.sleep(self.click_delay)

    def drag(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: float = 0.3,
    ) -> None:
        pyautogui.moveTo(start_x, start_y)
        pyautogui.dragTo(
            end_x,
            end_y,
            duration=duration,
            button="left",
        )

    def scroll(self, amount: int) -> None:
        pyautogui.scroll(amount)


if __name__ == "__main__":
    print("InputDriver Loaded")