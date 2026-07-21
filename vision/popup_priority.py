from __future__ import annotations

from typing import Iterable, Optional, Tuple

from vision.popup_models import PopupDetection, PopupState
from vision.popup_parser import PopupParser


class PopupPriorityResolver:
    """Selects popup work by semantic priority, then visual confidence."""

    def __init__(self, parser: Optional[PopupParser] = None) -> None:
        self.parser = parser or PopupParser()

    def rank(self, detections: Iterable[PopupDetection]) -> Tuple[PopupState, ...]:
        states = [self.parser.parse(item) for item in detections]
        states.sort(
            key=lambda item: (int(item.priority), item.confidence),
            reverse=True,
        )
        return tuple(states)

    def select(self, detections: Iterable[PopupDetection]) -> Optional[PopupState]:
        ranked = self.rank(detections)
        return ranked[0] if ranked else None
