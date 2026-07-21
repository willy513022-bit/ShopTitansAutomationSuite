from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np

from vision_core.ocr_engine import SharedOCREngine
from vision_core.preprocessing import (
    high_contrast_digits,
    upscale,
)


@dataclass(frozen=True)
class EnergyRecognitionResult:
    current: int | None
    maximum: int | None
    raw_text: str
    confidence: float

    @property
    def valid(self) -> bool:
        return (
            self.current is not None
            and self.maximum is not None
            and self.maximum > 0
            and 0 <= self.current <= self.maximum
        )


class EnergyRecognizer:
    PATTERNS = (
        re.compile(
            r"(?P<current>\d{1,7})\s*[/|]\s*(?P<maximum>\d{1,7})"
        ),
        re.compile(
            r"(?P<current>\d{1,7})\s+"
            r"(?P<maximum>\d{1,7})"
        ),
    )

    def __init__(
        self,
        ocr: SharedOCREngine | None = None,
    ) -> None:
        self.ocr = (
            ocr
            or SharedOCREngine()
        )

    def recognize(
        self,
        image: np.ndarray,
    ) -> EnergyRecognitionResult:
        candidates = [
            upscale(image, 4.0),
            high_contrast_digits(image),
        ]

        best_result = EnergyRecognitionResult(
            current=None,
            maximum=None,
            raw_text="",
            confidence=0.0,
        )

        for candidate in candidates:
            lines = self.ocr.read(candidate)

            raw_text = " ".join(
                line.text
                for line in lines
            )

            confidence = (
                sum(
                    line.confidence
                    for line in lines
                )
                / len(lines)
                if lines
                else 0.0
            )

            parsed = self._parse(
                raw_text
            )

            if (
                parsed.current is not None
                and confidence
                >= best_result.confidence
            ):
                best_result = (
                    EnergyRecognitionResult(
                        current=parsed.current,
                        maximum=parsed.maximum,
                        raw_text=raw_text,
                        confidence=confidence,
                    )
                )

        return best_result

    def _parse(
        self,
        text: str,
    ) -> EnergyRecognitionResult:
        normalized = (
            text
            .replace("O", "0")
            .replace("o", "0")
            .replace("I", "1")
            .replace("l", "1")
            .replace("\\", "/")
        )

        normalized = re.sub(
            r"[^0-9/| ]+",
            " ",
            normalized,
        )

        normalized = re.sub(
            r"\s+",
            " ",
            normalized,
        ).strip()

        for pattern in self.PATTERNS:
            match = pattern.search(
                normalized
            )

            if match is None:
                continue

            current = int(
                match.group("current")
            )

            maximum = int(
                match.group("maximum")
            )

            if maximum <= 0:
                continue

            if current > maximum:
                continue

            return EnergyRecognitionResult(
                current=current,
                maximum=maximum,
                raw_text=text,
                confidence=0.0,
            )

        return EnergyRecognitionResult(
            current=None,
            maximum=None,
            raw_text=text,
            confidence=0.0,
        )
