from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from vision.blueprint_progress_models import ImageRegion


@dataclass(frozen=True, slots=True)
class BlueprintNameOCRResult:
    text: str
    confidence: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0 and 1"
            )


@dataclass(frozen=True, slots=True)
class BlueprintNameDetection:
    card_region: ImageRegion
    name_region: ImageRegion

    ocr_text: str
    ocr_confidence: float

    item_name: Optional[str]

    match_score: Optional[float] = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.ocr_confidence <= 1.0:
            raise ValueError(
                "ocr_confidence must be between 0 and 1"
            )

        if (
            self.match_score is not None
            and not 0.0 <= self.match_score <= 1.0
        ):
            raise ValueError(
                "match_score must be between 0 and 1"
            )

    @property
    def detected(self) -> bool:
        return bool(self.item_name)