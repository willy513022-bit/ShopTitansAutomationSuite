from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class ClickTarget:
    """
    Runtime 可執行的點擊目標。

    所有 Vision / OCR / Template Matching
    最終都應該轉成 ClickTarget。
    """

    x: int
    y: int

    name: str = ""

    confidence: float = 1.0

    source: Optional[str] = None

    @property
    def position(self) -> tuple[int, int]:
        return (self.x, self.y)

    def __str__(self) -> str:
        label = self.name or "UnnamedTarget"
        return (
            f"{label} "
            f"({self.x}, {self.y}) "
            f"[{self.confidence:.2f}]"
        )

if __name__ == "__main__":
    target = ClickTarget(
        x=500,
        y=300,
        name="Reconnect Button",
        confidence=0.98,
        source="template_matching",
    )

    print(target)
    print(target.position)