from vision.popup_models import (
    PopupActionType,
    PopupDetection,
    PopupPriority,
    PopupType,
)
from vision.popup_parser import PopupParser


def make_detection(popup_type: PopupType) -> PopupDetection:
    return PopupDetection(
        popup_type=popup_type,
        confidence=0.95,
        template_id=f"{popup_type.value}_variant",
    )


def test_reconnect_parsing_and_action():
    parser = PopupParser()
    state = parser.parse(make_detection(PopupType.RECONNECT))
    action = parser.action_for(state)

    assert state.reconnect_required is True
    assert state.priority is PopupPriority.RECONNECT
    assert action.action_type is PopupActionType.RECONNECT
    assert action.target_name == "reconnect_button"


def test_paid_offer_parsing_and_action():
    parser = PopupParser()
    state = parser.parse(make_detection(PopupType.PAID_OFFER))
    action = parser.action_for(state)

    assert state.paid_offer_visible is True
    assert action.action_type is PopupActionType.CLOSE_OFFER
    assert action.target_name == "offer_close_button"


def test_upgrade_parsing_and_action():
    parser = PopupParser()
    state = parser.parse(make_detection(PopupType.UPGRADE_FINISHED))
    action = parser.action_for(state)

    assert state.upgrade_finished is True
    assert action.action_type is PopupActionType.COLLECT_UPGRADE
