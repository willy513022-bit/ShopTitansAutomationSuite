import pytest

from vision.popup_models import (
    PopupAction,
    PopupActionType,
    PopupDetection,
    PopupPriority,
    PopupState,
    PopupType,
)


def test_popup_detection_validation():
    detection = PopupDetection(
        popup_type=PopupType.RECONNECT,
        confidence=0.98,
        template_id="error_1000",
    )
    assert detection.popup_type is PopupType.RECONNECT
    assert detection.template_id == "error_1000"


def test_popup_detection_rejects_bad_confidence():
    with pytest.raises(ValueError):
        PopupDetection(
            popup_type=PopupType.PAID_OFFER,
            confidence=1.1,
            template_id="offer",
        )


def test_popup_state_semantic_properties():
    state = PopupState(
        popup_type=PopupType.UPGRADE_FINISHED,
        priority=PopupPriority.UPGRADE_FINISHED,
        blocking=True,
        confidence=0.9,
        source_template_id="complete_1",
    )
    assert state.upgrade_finished is True
    assert state.reconnect_required is False
    assert state.paid_offer_visible is False


def test_popup_action_validation():
    action = PopupAction(
        action_type=PopupActionType.CLOSE_OFFER,
        popup_type=PopupType.PAID_OFFER,
        target_name="offer_close_button",
        priority=PopupPriority.PAID_OFFER,
        confidence=0.92,
    )
    assert action.action_type is PopupActionType.CLOSE_OFFER
