from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

import cv2
import numpy as np

from vision.match_result import MatchResult


ImageInput = Union[str, Path, np.ndarray]


class TemplateMatcher:
    def __init__(self, threshold: float = 0.85):
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be between 0 and 1")
        self.threshold = threshold

    def match(
        self,
        screenshot: ImageInput,
        template: ImageInput,
        template_name: str = "template",
    ) -> MatchResult:
        screen = self._load_image(screenshot)
        target = self._load_image(template)

        if screen is None:
            raise ValueError("Unable to load screenshot")
        if target is None:
            raise ValueError("Unable to load template")

        screen_gray = self._to_gray(screen)
        target_gray = self._to_gray(target)

        screen_h, screen_w = screen_gray.shape[:2]
        target_h, target_w = target_gray.shape[:2]

        if target_h > screen_h or target_w > screen_w:
            return MatchResult(template_name=template_name, confidence=0.0)

        result = cv2.matchTemplate(
            screen_gray,
            target_gray,
            cv2.TM_CCOEFF_NORMED,
        )
        _, max_value, _, max_location = cv2.minMaxLoc(result)

        confidence = float(max_value)
        if confidence < self.threshold:
            return MatchResult(
                template_name=template_name,
                confidence=confidence,
            )

        return MatchResult(
            template_name=template_name,
            confidence=confidence,
            location=(int(max_location[0]), int(max_location[1])),
            size=(int(target_w), int(target_h)),
        )

    @staticmethod
    def _load_image(value: ImageInput) -> Optional[np.ndarray]:
        if isinstance(value, np.ndarray):
            return value.copy()

        return cv2.imread(str(value), cv2.IMREAD_COLOR)

    @staticmethod
    def _to_gray(image: np.ndarray) -> np.ndarray:
        if image.ndim == 2:
            return image
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
