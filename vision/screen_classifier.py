from __future__ import annotations

from typing import Dict, Optional, Union

from core.screen_state import ScreenState
from vision.screen_detector import ScreenDetection


class ScreenClassifier:
    DEFAULT_MAPPING: Dict[str, ScreenState] = {
        "town": ScreenState.TOWN,
        "loading": ScreenState.LOADING,
        "disconnected": ScreenState.DISCONNECTED,
        "welcome_back": ScreenState.WELCOME_BACK,
        "limited_offer": ScreenState.LIMITED_OFFER,
    }

    def __init__(
        self,
        mapping: Optional[Dict[str, ScreenState]] = None,
        unknown_state: ScreenState = ScreenState.UNKNOWN,
    ):
        self.mapping = dict(self.DEFAULT_MAPPING)
        if mapping:
            self.mapping.update(mapping)
        self.unknown_state = unknown_state

    def classify(
        self,
        detection: Optional[Union[ScreenDetection, str]],
    ) -> ScreenState:
        if detection is None:
            return self.unknown_state

        screen_name = (
            detection.screen_name
            if isinstance(detection, ScreenDetection)
            else str(detection)
        )
        return self.mapping.get(screen_name, self.unknown_state)
