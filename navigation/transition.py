from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .screen import Screen


class TransitionAction(str, Enum):
    # Direct entry points from the Shop screen.
    OPEN_CRAFT = "OPEN_CRAFT"
    OPEN_FUSION = "OPEN_FUSION"

    # Switching is still useful when already inside production UI.
    SWITCH_TO_CRAFT = "SWITCH_TO_CRAFT"
    SWITCH_TO_FUSION = "SWITCH_TO_FUSION"

    BACK = "BACK"

    OPEN_QUEST = "OPEN_QUEST"
    OPEN_GUILD = "OPEN_GUILD"
    OPEN_PET = "OPEN_PET"
    OPEN_UPGRADE = "OPEN_UPGRADE"
    OPEN_KING = "OPEN_KING"

    CLOSE_MODAL = "CLOSE_MODAL"


@dataclass(frozen=True)
class Transition:
    source: Screen
    target: Screen
    action: TransitionAction
    cost: int = 1

    def validate(self) -> None:
        if self.source == self.target:
            raise ValueError(
                "transition source and target must differ"
            )

        if self.cost <= 0:
            raise ValueError(
                "transition cost must be positive"
            )