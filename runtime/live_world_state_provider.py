from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np

from runtime.popup_coordinate import popup_center_to_screen
from runtime.target_resolver import TargetResolver
from runtime.target_updater import TargetUpdater
from vision.capture import screenshot
from vision.popup_detector import PopupDetector
from vision.popup_models import PopupDetection, PopupState, PopupType
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
        - 動態 ClickTarget 更新
    """

    def __init__(
        self,
        window_title: str = "Shop Titans",
        project_root: Optional[Path] = None,
        vision_engine: Optional[VisionEngine] = None,
        popup_detector: Optional[PopupDetector] = None,
        popup_parser: Optional[PopupParser] = None,
        world_state_builder: Optional[WorldStateBuilder] = None,
        target_resolver: Optional[TargetResolver] = None,
        target_updater: Optional[TargetUpdater] = None,
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
        self._builder = (
            world_state_builder or WorldStateBuilder()
        )

        self._target_resolver = (
            target_resolver or TargetResolver()
        )
        self._target_updater = (
            target_updater
            or TargetUpdater(self._target_resolver)
        )

        self._last_frame: Optional[np.ndarray] = None
        self._last_popup_detection: Optional[
            PopupDetection
        ] = None
        self._templates_registered = False

    @property
    def window_title(self) -> str:
        return self._window_title

    @property
    def project_root(self) -> Path:
        return self._project_root

    @property
    def target_resolver(self) -> TargetResolver:
        """
        回傳 Provider 使用的 TargetResolver。

        RuntimeExecutor 必須共用同一個 Resolver，
        才能取得 Vision 即時更新的點擊座標。
        """

        return self._target_resolver

    @property
    def last_frame(self) -> Optional[np.ndarray]:
        """
        回傳最近一次成功擷取畫面的複本。

        尚未擷取成功時回傳 None。
        """

        if self._last_frame is None:
            return None

        return self._last_frame.copy()

    @property
    def last_popup_detection(
        self,
    ) -> Optional[PopupDetection]:
        return self._last_popup_detection

    def __call__(self) -> WorldState:
        return self.build()

    def capture_frame(self) -> np.ndarray:
        """擷取目前的 Shop Titans 視窗。"""

        frame = screenshot(self._window_title)

        if frame is None:
            raise RuntimeError(
                "Unable to capture window: "
                f"{self._window_title!r}"
            )

        if (
            not isinstance(frame, np.ndarray)
            or frame.size == 0
        ):
            raise RuntimeError(
                "Capture returned an invalid frame"
            )

        self._last_frame = frame.copy()

        return frame

    def register_popup_templates(self) -> int:
        """
        載入 assets/popups 裡的所有 PNG 模板。

        同一個 Provider 執行期間只載入一次。
        """

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
                print(
                    "[LiveWorldStateProvider] "
                    "Template directory missing: "
                    f"{directory}"
                )
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

    def update_popup_target(
        self,
        detection: PopupDetection,
        frame: np.ndarray,
    ) -> None:
        """
        將可點擊的 PopupDetection 轉換成 ClickTarget。

        目前只有 reconnect_button 經過真機驗證。
        付費優惠和升級完成仍需準備按鈕小模板，
        不能直接點擊整張 Popup 的中心。
        """

        if detection.template_id != "reconnect_button":
            return

        popup_state = self._popup_parser.parse(detection)
        popup_action = self._popup_parser.action_for(
            popup_state
        )

        if popup_action.target_name != "reconnect_button":
            return

        screen_x, screen_y = popup_center_to_screen(
            popup=detection,
            frame=frame,
            window_title=self._window_title,
        )

        self._target_updater.update_popup_target(
            detection=detection,
            target_name=popup_action.target_name,
            screen_x=screen_x,
            screen_y=screen_y,
        )

    def build(self) -> WorldState:
        """擷取並分析最新畫面，建立 WorldState。"""

        frame = self.capture_frame()

        self.register_popup_templates()

        vision_result = self._vision_engine.analyze(
            frame
        )

        popup_detection = (
            self._popup_detector.detect_best(frame)
        )

        self._last_popup_detection = popup_detection

        popup_state: Optional[PopupState] = None

        if popup_detection is not None:
            popup_state = self._popup_parser.parse(
                popup_detection
            )

            self.update_popup_target(
                detection=popup_detection,
                frame=frame,
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
                "popup_location": (
                    popup_detection.location
                    if popup_detection is not None
                    else None
                ),
                "popup_size": (
                    popup_detection.size
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