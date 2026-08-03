from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np

from vision.capture import screenshot
from vision.popup_detector import PopupDetector
from vision.popup_models import PopupState, PopupType
from vision.popup_parser import PopupParser
from vision.vision_engine import VisionEngine
from world_state.world_state import WorldState
from world_state.world_state_builder import WorldStateBuilder


class LiveWorldStateProvider:
    """
    從真實 Shop Titans 視窗建立 WorldState。

    目前整合：
        - 真實畫面擷取
        - Screen Vision
        - Popup Detection
        - Popup Parsing
        - WorldStateBuilder
    """

    def __init__(
        self,
        window_title: str = "Shop Titans",
        project_root: Optional[Path] = None,
        vision_engine: Optional[VisionEngine] = None,
        popup_detector: Optional[PopupDetector] = None,
        popup_parser: Optional[PopupParser] = None,
        world_state_builder: Optional[WorldStateBuilder] = None,
    ) -> None:
        title = window_title.strip()

        if not title:
            raise ValueError("window_title is required")

        self._window_title = title
        self._project_root = (
            project_root
            if project_root is not None
            else Path(__file__).resolve().parents[1]
        )

        self._vision_engine = vision_engine or VisionEngine()
        self._popup_detector = popup_detector or PopupDetector()
        self._popup_parser = popup_parser or PopupParser()
        self._builder = world_state_builder or WorldStateBuilder()

        self._last_frame: Optional[np.ndarray] = None
        self._templates_registered = False

    @property
    def window_title(self) -> str:
        return self._window_title

    @property
    def last_frame(self) -> Optional[np.ndarray]:
        if self._last_frame is None:
            return None

        return self._last_frame.copy()

    def __call__(self) -> WorldState:
        return self.build()

    def capture_frame(self) -> np.ndarray:
        frame = screenshot(self._window_title)

        if frame is None:
            raise RuntimeError(
                f"Unable to capture window: {self._window_title!r}"
            )

        if not isinstance(frame, np.ndarray) or frame.size == 0:
            raise RuntimeError("Capture returned an invalid frame")

        self._last_frame = frame.copy()

        return frame

    def register_popup_templates(self) -> int:
        if self._templates_registered:
            return 0

        directories = {
            PopupType.RECONNECT: (
                self._project_root
                / "assets"
                / "popups"
                / "reconnect"
            ),
            PopupType.PAID_OFFER: (
                self._project_root
                / "assets"
                / "popups"
                / "paid_offer"
            ),
            PopupType.UPGRADE_FINISHED: (
                self._project_root
                / "assets"
                / "popups"
                / "upgrade_finished"
            ),
        }

        registered_count = 0

        for popup_type, directory in directories.items():
            if not directory.exists():
                continue

            for path in sorted(directory.glob("*.png")):
                self._popup_detector.register_file(
                    popup_type=popup_type,
                    path=path,
                    template_id=path.stem,
                )
                registered_count += 1

        self._templates_registered = True

        return registered_count

    def build(self) -> WorldState:
        frame = self.capture_frame()

        self.register_popup_templates()

        vision_result = self._vision_engine.analyze(frame)

        popup_detection = self._popup_detector.detect_best(frame)

        popup_state: Optional[PopupState] = None

        if popup_detection is not None:
            popup_state = self._popup_parser.parse(
                popup_detection
            )

        world_state = self._builder.build(
            vision_result=vision_result,
            popup_state=popup_state,
        )

        height, width = frame.shape[:2]

        metadata = dict(world_state.metadata)
        metadata.update(
            {
                "capture_width": width,
                "capture_height": height,
                "window_title": self._window_title,
                "popup_template_id": (
                    popup_detection.template_id
                    if popup_detection is not None
                    else None
                ),
                "popup_confidence": (
                    popup_detection.confidence
                    if popup_detection is not None
                    else None
                ),
            }
        )

        return WorldState(
            notifications=world_state.notifications,
            popup=world_state.popup,
            inventory=world_state.inventory,
            production=world_state.production,
            recipes=world_state.recipes,
            screen=world_state.screen,
            observed_at=world_state.observed_at,
            metadata=metadata,
        )