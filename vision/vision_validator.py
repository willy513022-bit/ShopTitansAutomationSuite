from __future__ import annotations

from typing import Callable

import numpy as np

from core.screen_state import ScreenState
from vision.vision_engine import VisionEngine


class VisionValidator:
    def __init__(
        self,
        vision_engine: VisionEngine,
        screenshot_provider: Callable[[], np.ndarray],
    ):
        self.vision_engine = vision_engine
        self.screenshot_provider = screenshot_provider

    def validate(self, expected: ScreenState) -> bool:
        screenshot = self.screenshot_provider()
        result = self.vision_engine.analyze(screenshot)
        return result.screen_state == expected

    def validate_decision(self, decision: dict) -> bool:
        expected = decision.get("expected")
        if expected is None:
            return False
        return self.validate(expected)
