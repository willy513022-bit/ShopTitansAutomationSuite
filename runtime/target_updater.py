from __future__ import annotations

from runtime.click_target import ClickTarget
from runtime.target_resolver import TargetResolver
from vision.popup_models import PopupDetection


class TargetUpdater:
    """將 Vision 偵測結果同步到 Runtime TargetResolver。"""

    def __init__(self, resolver: TargetResolver) -> None:
        self._resolver = resolver

    def update_popup_target(
        self,
        detection: PopupDetection,
        target_name: str,
        screen_x: int,
        screen_y: int,
    ) -> ClickTarget:
        normalized_name = target_name.strip()

        if not normalized_name:
            raise ValueError("target_name is required")

        target = ClickTarget(
            x=int(screen_x),
            y=int(screen_y),
            name=normalized_name,
            confidence=detection.confidence,
            source=detection.template_id,
        )

        # 必須使用 PopupAction 的 target_name 註冊，
        # 例如 reconnect_button，而不是任意模板檔名。
        self._resolver.register(
            normalized_name,
            target,
        )

        return target