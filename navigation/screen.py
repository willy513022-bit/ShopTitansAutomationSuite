from __future__ import annotations

from enum import Enum


class Screen(str, Enum):
    UNKNOWN = "UNKNOWN"

    SHOP = "SHOP"

    PRODUCTION = "PRODUCTION"
    CRAFT = "CRAFT"
    FUSION = "FUSION"

    QUEST = "QUEST"
    GUILD = "GUILD"
    PET = "PET"
    UPGRADE = "UPGRADE"
    KING = "KING"

    MODAL = "MODAL"
