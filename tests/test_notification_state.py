import pytest

from vision.notification_models import (
    NotificationCategory,
    ProductionNotification,
    QuestNotification,
)
from world_state import NotificationState


def test_notification_state_exposes_categories():
    craft = ProductionNotification(NotificationCategory.CRAFT, 2, False, 0.9)
    quest = QuestNotification(0, True, 0.8)
    state = NotificationState({NotificationCategory.CRAFT: craft, "quest": quest})
    assert state.craft is craft
    assert state.quest is quest
    assert state.fusion is None
    assert state.any_visible is True


def test_notification_state_rejects_wrong_semantic_type():
    with pytest.raises(TypeError):
        NotificationState({NotificationCategory.CRAFT: QuestNotification(1, False, 0.9)})
