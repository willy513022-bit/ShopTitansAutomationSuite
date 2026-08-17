from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from vision.blueprint_card_locator import (
    BlueprintCard,
)
from vision.blueprint_name_detector import (
    BlueprintNameDetector,
)
from vision.blueprint_progress_detector import (
    BlueprintProgressDetector,
)
from vision.blueprint_progress_models import (
    ImageRegion,
)


@dataclass(frozen=True, slots=True)
class BlueprintCardState:
    """
    一張 Blueprint Craft 卡片的統一視覺狀態。

    這個模型是 Vision 和 Planner 之間的橋樑。

    Planner 不需要知道：
    - OCR 怎麼做
    - 名稱框在哪
    - Progress 框在哪
    - RapidOCR 回傳格式

    Planner 只需要知道：
    - 這是什麼物品
    - 目前里程碑是多少
    - 還差多少件
    """

    row: int
    column: int

    card_region: ImageRegion

    item_name: Optional[str]

    current_progress: Optional[int]
    current_target: Optional[int]
    remaining: Optional[int]

    name_confidence: float
    progress_confidence: float

    name_match_score: Optional[float] = None

    name_ocr_text: str = ""
    progress_ocr_text: str = ""

    def __post_init__(self) -> None:
        if self.row < 0:
            raise ValueError(
                "row cannot be negative"
            )

        if self.column < 0:
            raise ValueError(
                "column cannot be negative"
            )

        if not (
            0.0 <= self.name_confidence <= 1.0
        ):
            raise ValueError(
                "name_confidence must be between 0 and 1"
            )

        if not (
            0.0
            <= self.progress_confidence
            <= 1.0
        ):
            raise ValueError(
                "progress_confidence must be between 0 and 1"
            )

        if (
            self.name_match_score is not None
            and not (
                0.0
                <= self.name_match_score
                <= 1.0
            )
        ):
            raise ValueError(
                "name_match_score must be between 0 and 1"
            )

        progress_values = (
            self.current_progress,
            self.current_target,
            self.remaining,
        )

        # Progress 必須全部存在或全部不存在。
        if any(
            value is None
            for value in progress_values
        ):
            if not all(
                value is None
                for value in progress_values
            ):
                raise ValueError(
                    "progress values must all be set "
                    "or all be None"
                )

        if (
            self.current_progress is not None
            and self.current_target is not None
            and self.remaining is not None
        ):
            if self.current_progress < 0:
                raise ValueError(
                    "current_progress cannot be negative"
                )

            if self.current_target <= 0:
                raise ValueError(
                    "current_target must be positive"
                )

            if (
                self.current_progress
                > self.current_target
            ):
                raise ValueError(
                    "current_progress cannot exceed "
                    "current_target"
                )

            expected_remaining = (
                self.current_target
                - self.current_progress
            )

            if (
                self.remaining
                != expected_remaining
            ):
                raise ValueError(
                    "remaining does not match "
                    "current_target - current_progress"
                )

    @property
    def has_name(self) -> bool:
        return bool(self.item_name)

    @property
    def has_progress(self) -> bool:
        return (
            self.current_progress is not None
            and self.current_target is not None
            and self.remaining is not None
        )

    @property
    def valid(self) -> bool:
        """
        一張卡片只有「名稱 + Progress」都有，
        才能安全交給後續 Planner。
        """

        return (
            self.has_name
            and self.has_progress
        )

    @property
    def milestone_complete(self) -> bool:
        return bool(
            self.has_progress
            and self.remaining == 0
        )

    @property
    def progress_text(self) -> str:
        if not self.has_progress:
            return "?/?"

        return (
            f"{self.current_progress}"
            f"/"
            f"{self.current_target}"
        )


class BlueprintCardScanner:
    """
    將 BlueprintCard Locator 產生的卡片區域，
    轉換成可供 Planner 使用的 BlueprintCardState。

    Scanner 不負責找卡片。

    流程：

        BlueprintCard
             ↓
        NameDetector
             +
        ProgressDetector
             ↓
        BlueprintCardState
    """

    def __init__(
        self,
        *,
        name_detector: BlueprintNameDetector,
        progress_detector: BlueprintProgressDetector
        | None = None,
    ) -> None:
        if not isinstance(
            name_detector,
            BlueprintNameDetector,
        ):
            raise TypeError(
                "name_detector must be BlueprintNameDetector"
            )

        if (
            progress_detector is not None
            and not isinstance(
                progress_detector,
                BlueprintProgressDetector,
            )
        ):
            raise TypeError(
                "progress_detector must be "
                "BlueprintProgressDetector"
            )

        self.name_detector = name_detector

        self.progress_detector = (
            progress_detector
            or BlueprintProgressDetector()
        )

    def scan_card(
        self,
        *,
        image: np.ndarray,
        card: BlueprintCard,
    ) -> BlueprintCardState:
        if not isinstance(
            image,
            np.ndarray,
        ):
            raise TypeError(
                "image must be numpy.ndarray"
            )

        if image.size == 0:
            raise ValueError(
                "image cannot be empty"
            )

        if not isinstance(
            card,
            BlueprintCard,
        ):
            raise TypeError(
                "card must be BlueprintCard"
            )

        name_detection = (
            self.name_detector.detect(
                image=image,
                card_region=card.region,
            )
        )

        progress_detection = (
            self.progress_detector.detect(
                image=image,
                card_region=card.region,
            )
        )

        current_progress = None
        current_target = None
        remaining = None

        if (
            progress_detection.parsed
            is not None
        ):
            current_progress = (
                progress_detection
                .parsed
                .current_progress
            )

            current_target = (
                progress_detection
                .parsed
                .current_target
            )

            remaining = (
                progress_detection
                .parsed
                .remaining
            )

        return BlueprintCardState(
            row=card.row,
            column=card.column,
            card_region=card.region,
            item_name=(
                name_detection.item_name
            ),
            current_progress=current_progress,
            current_target=current_target,
            remaining=remaining,
            name_confidence=(
                name_detection.ocr_confidence
            ),
            progress_confidence=(
                progress_detection
                .ocr_confidence
            ),
            name_match_score=(
                name_detection.match_score
            ),
            name_ocr_text=(
                name_detection.ocr_text
            ),
            progress_ocr_text=(
                progress_detection.ocr_text
            ),
        )

    def scan(
        self,
        *,
        image: np.ndarray,
        cards: list[BlueprintCard],
    ) -> tuple[BlueprintCardState, ...]:
        if not isinstance(
            image,
            np.ndarray,
        ):
            raise TypeError(
                "image must be numpy.ndarray"
            )

        if image.size == 0:
            raise ValueError(
                "image cannot be empty"
            )

        states: list[
            BlueprintCardState
        ] = []

        for card in cards:
            states.append(
                self.scan_card(
                    image=image,
                    card=card,
                )
            )

        return tuple(states)