from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from core.screen_state import ScreenState
from vision.screen_classifier import ScreenClassifier
from vision.screen_detector import ScreenDetection, ScreenDetector


@dataclass(frozen=True)
class VisionResult:
    screen_state: ScreenState
    confidence: float
    detection: Optional[ScreenDetection]


class VisionEngine:
    def __init__(
        self,
        detector: Optional[ScreenDetector] = None,
        classifier: Optional[ScreenClassifier] = None,
    ):
        self.detector = detector or ScreenDetector()
        self.classifier = classifier or ScreenClassifier()

    def analyze(self, screenshot: np.ndarray) -> VisionResult:
        detection = self.detector.detect(screenshot)
        state = self.classifier.classify(detection)
        confidence = 0.0 if detection is None else detection.confidence

        return VisionResult(
            screen_state=state,
            confidence=confidence,
            detection=detection,
        )
