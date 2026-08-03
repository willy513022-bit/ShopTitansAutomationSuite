from __future__ import annotations


class MockInputDriver:
    """
    測試用 InputDriver。

    不會真的控制滑鼠，只會記錄執行過的操作。
    """

    def __init__(self) -> None:
        self.clicks: list[tuple[int, int]] = []

    def click(self, x: int, y: int) -> None:
        self.clicks.append((x, y))
        print(f"[MockInputDriver] click({x}, {y})")