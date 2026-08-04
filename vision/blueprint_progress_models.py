from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from services.blueprint_progress_parser import (
    ParsedBlueprintProgress,
)


@dataclass(frozen=True, slots=True)
class ImageRegion:
    """
    影像中的矩形區域。

    座標皆相對於傳入的完整影像。
    """

    x: int
    y: int
    width: int
    height: int

    def __post_init__(self) -> None:
        if self.x < 0:
            raise ValueError("x cannot be negative")

        if self.y < 0:
            raise ValueError("y cannot be negative")

        if self.width <= 0:
            raise ValueError(
                "width must be greater than 0"
            )

        if self.height <= 0:
            raise ValueError(
                "height must be greater than 0"
            )

    @property
    def left(self) -> int:
        return self.x

    @property
    def top(self) -> int:
        return self.y

    @property
    def right(self) -> int:
        return self.x + self.width

    @property
    def bottom(self) -> int:
        return self.y + self.height

    @property
    def center(self) -> tuple[int, int]:
        return (
            self.x + self.width // 2,
            self.y + self.height // 2,
        )


@dataclass(frozen=True, slots=True)
class BlueprintProgressOCRResult:
    """
    OCR 原始輸出。
    """

    text: str
    confidence: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0 and 1"
            )


@dataclass(frozen=True, slots=True)
class BlueprintProgressDetection:
    """
    BlueprintProgressDetector 的完整結果。
    """

    card_region: ImageRegion
    progress_region: ImageRegion
    ocr_text: str
    ocr_confidence: float
    parsed: Optional[ParsedBlueprintProgress]

    def __post_init__(self) -> None:
        if not 0.0 <= self.ocr_confidence <= 1.0:
            raise ValueError(
                "ocr_confidence must be between 0 and 1"
            )

    @property
    def detected(self) -> bool:
        return self.parsed is not None

    @property
    def current_progress(self) -> Optional[int]:
        if self.parsed is None:
            return None

        return self.parsed.current_progress

    @property
    def current_target(self) -> Optional[int]:
        if self.parsed is None:
            return None

        return self.parsed.current_target

    @property
    def remaining(self) -> Optional[int]:
        if self.parsed is None:
            return None

        return self.parsed.remaining

    @property
    def complete(self) -> bool:
        return bool(
            self.parsed
            and self.parsed.complete
        )