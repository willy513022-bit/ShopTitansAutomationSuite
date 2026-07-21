from __future__ import annotations

from vision.popup_models import (
    PopupAction,
    PopupActionType,
    PopupDetection,
    PopupPriority,
    PopupState,
    PopupType,
)


class PopupParser:
    """Converts raw popup detections into semantic state and runtime intent."""

    _PRIORITIES = {
        PopupType.RECONNECT: PopupPriority.RECONNECT,
        PopupType.PAID_OFFER: PopupPriority.PAID_OFFER,
        PopupType.UPGRADE_FINISHED: PopupPriority.UPGRADE_FINISHED,
    }

    _ACTIONS = {
        PopupType.RECONNECT: (PopupActionType.RECONNECT, "reconnect_button"),
        PopupType.PAID_OFFER: (PopupActionType.CLOSE_OFFER, "offer_close_button"),
        PopupType.UPGRADE_FINISHED: (
            PopupActionType.COLLECT_UPGRADE,
            "upgrade_complete_button",
        ),
    }

    def parse(self, detection: PopupDetection) -> PopupState:
        return PopupState(
            popup_type=detection.popup_type,
            priority=self._PRIORITIES[detection.popup_type],
            blocking=True,
            confidence=detection.confidence,
            source_template_id=detection.template_id,
        )

    def action_for(self, state: PopupState) -> PopupAction:
        action_type, target_name = self._ACTIONS[state.popup_type]
        return PopupAction(
            action_type=action_type,
            popup_type=state.popup_type,
            target_name=target_name,
            priority=state.priority,
            confidence=state.confidence,
        )
