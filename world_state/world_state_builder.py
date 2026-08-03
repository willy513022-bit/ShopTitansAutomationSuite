from __future__ import annotations

from typing import Optional

from vision.popup_models import PopupState
from vision.vision_engine import VisionResult

from .world_state import WorldState


class WorldStateBuilder:
    """
    將各 Vision 模組的結果組裝成 Runtime 使用的 WorldState。
    """

    def build(
        self,
        vision_result: VisionResult,
        popup_state: Optional[PopupState] = None,
    ) -> WorldState:

        detection = vision_result.detection

        screen_name = (
            detection.screen_name
            if detection is not None
            else None
        )

        return WorldState(
            popup=popup_state,
            screen=screen_name,
        )