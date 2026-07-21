from vision.popup_models import PopupDetection, PopupType
from vision.popup_priority import PopupPriorityResolver


def detection(popup_type: PopupType, confidence: float) -> PopupDetection:
    return PopupDetection(
        popup_type=popup_type,
        confidence=confidence,
        template_id=f"{popup_type.value}_test",
    )


def test_reconnect_wins_even_with_lower_confidence():
    resolver = PopupPriorityResolver()
    selected = resolver.select(
        [
            detection(PopupType.UPGRADE_FINISHED, 0.99),
            detection(PopupType.PAID_OFFER, 0.98),
            detection(PopupType.RECONNECT, 0.86),
        ]
    )
    assert selected is not None
    assert selected.popup_type is PopupType.RECONNECT


def test_confidence_breaks_same_priority_ties():
    resolver = PopupPriorityResolver()
    ranked = resolver.rank(
        [
            detection(PopupType.PAID_OFFER, 0.87),
            detection(PopupType.PAID_OFFER, 0.96),
        ]
    )
    assert ranked[0].confidence == 0.96


def test_empty_input_returns_none():
    assert PopupPriorityResolver().select([]) is None
