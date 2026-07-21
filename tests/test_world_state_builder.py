from vision.notification_models import NotificationCategory, NotificationDetection
from vision.popup_models import PopupDetection, PopupType
from world_state import InventoryState, ProductionState, WorldStateBuilder


def notification(category, badge, confidence):
    return NotificationDetection(category, badge, confidence, confidence, confidence)


def popup(kind, confidence, template):
    return PopupDetection(kind, confidence, template)


def test_builder_parses_notifications_and_keeps_best_per_category():
    state = WorldStateBuilder().build(
        notification_detections=[
            notification(NotificationCategory.CRAFT, "1", 0.70),
            notification(NotificationCategory.CRAFT, "+", 0.95),
            notification(NotificationCategory.QUEST, "+", 0.88),
        ],
        inventory=InventoryState({"Wood Axe": 4}),
        production=ProductionState(2),
        screen="shop",
    )
    assert state.notifications.craft.empty_slot_available is True
    assert state.notifications.quest.new_available is True
    assert state.inventory.quantity("Wood Axe") == 4
    assert state.production.free_slots == 2
    assert state.screen == "shop"


def test_builder_resolves_popup_by_semantic_priority():
    state = WorldStateBuilder().build(
        popup_detections=[
            popup(PopupType.PAID_OFFER, 0.99, "offer"),
            popup(PopupType.RECONNECT, 0.70, "disconnect"),
        ]
    )
    assert state.popup.popup_type is PopupType.RECONNECT
    assert state.has_blocking_popup is True


def test_builder_empty_observation_is_safe_for_gameplay():
    state = WorldStateBuilder().build()
    assert state.notifications.any_visible is False
    assert state.popup is None
    assert state.safe_for_gameplay is True


def test_builder_copies_metadata():
    metadata = {"frame_id": 12}
    state = WorldStateBuilder().build(metadata=metadata)
    metadata["frame_id"] = 99
    assert state.metadata["frame_id"] == 12
