from __future__ import annotations

from typing import Dict

from .click_target import ClickTarget


class TargetResolver:
    """
    將 Runtime 的 target_name
    轉換成可執行的 ClickTarget。

    第一版先使用固定座標，
    後續再改成 Template Matching / OCR。
    """

    def __init__(self) -> None:
        self._targets: Dict[str, ClickTarget] = {}

    def register(self, name: str, target: ClickTarget) -> None:
        self._targets[name] = target

    def resolve(self, name: str) -> ClickTarget:
        if name not in self._targets:
            raise KeyError(f"Unknown target: {name}")

        return self._targets[name]


if __name__ == "__main__":
    resolver = TargetResolver()

    resolver.register(
        "reconnect_button",
        ClickTarget(
            x=500,
            y=300,
            name="Reconnect Button",
        ),
    )

    target = resolver.resolve("reconnect_button")

    print(target)