from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Mapping, Optional


class PopupType(str, Enum):
    """Semantic popup families supported by the Vision layer."""

    RECONNECT = "reconnect"
    PAID_OFFER = "paid_offer"
    UPGRADE_FINISHED = "upgrade_finished"


class PopupPriority(IntEnum):
    """Higher values are handled before lower values."""

    UPGRADE_FINISHED = 100
    PAID_OFFER = 200
    RECONNECT = 300


class PopupActionType(str, Enum):
    RECONNECT = "reconnect"
    CLOSE_OFFER = "close_offer"
    COLLECT_UPGRADE = "collect_upgrade"


@dataclass(frozen=True)
class PopupDetection:
    """Raw visual fact produced by :class:`PopupDetector`."""

    popup_type: PopupType
    confidence: float
    template_id: str
    location: Optional[tuple[int, int]] = None
    size: Optional[tuple[int, int]] = None
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        template_id = self.template_id.strip()
        if not template_id:
            raise ValueError("template_id is required")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        object.__setattr__(self, "template_id", template_id)


@dataclass(frozen=True)
class PopupState:
    """Semantic state consumed by WorldState and Planner layers."""

    popup_type: PopupType
    priority: PopupPriority
    blocking: bool
    confidence: float
    source_template_id: str

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if not self.source_template_id.strip():
            raise ValueError("source_template_id is required")

    @property
    def reconnect_required(self) -> bool:
        return self.popup_type is PopupType.RECONNECT

    @property
    def paid_offer_visible(self) -> bool:
        return self.popup_type is PopupType.PAID_OFFER

    @property
    def upgrade_finished(self) -> bool:
        return self.popup_type is PopupType.UPGRADE_FINISHED


@dataclass(frozen=True)
class PopupAction:
    """Runtime-neutral instruction derived from a popup state."""

    action_type: PopupActionType
    popup_type: PopupType
    target_name: str
    priority: PopupPriority
    confidence: float

    def __post_init__(self) -> None:
        if not self.target_name.strip():
            raise ValueError("target_name is required")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
