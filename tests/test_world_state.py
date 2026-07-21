from datetime import datetime

import pytest

from vision.popup_models import PopupPriority, PopupState, PopupType
from world_state import InventoryState, WorldState


def test_world_state_freezes_metadata_and_reports_blocking_popup():
    metadata = {"source": "vision"}
    popup = PopupState(PopupType.RECONNECT, PopupPriority.RECONNECT, True, 0.9, "r1")
    state = WorldState(popup=popup, inventory=InventoryState({"Wood": 3}), metadata=metadata)
    metadata["source"] = "changed"
    assert state.metadata["source"] == "vision"
    assert state.has_blocking_popup is True
    assert state.safe_for_gameplay is False


def test_world_state_rejects_naive_time():
    with pytest.raises(ValueError):
        WorldState(observed_at=datetime(2026, 7, 21, 12, 0, 0))
