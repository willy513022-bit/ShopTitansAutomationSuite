from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class PlayerProfile:
    """Player-specific strategy settings.

    This class intentionally contains player preferences only.
    General Shop Titans mechanics belong in the game knowledge layer.
    """

    mode: str = "COLLECTOR"
    collection: Dict[str, Any] = field(default_factory=lambda: {
        "keep_legendary_forever": True,
        "keep_non_normal_until_collection_complete": True,
        "permanent_keep_items": [],
    })
    pet: Dict[str, Any] = field(default_factory=lambda: {
        "food_quality": "NORMAL",
    })
    king: Dict[str, Any] = field(default_factory=lambda: {
        "mode": "MANUAL",
        "auto_sell": False,
    })
    upgrade: Dict[str, Any] = field(default_factory=lambda: {
        "max_parallel": 2,
        "use_gems": False,
        "request_guild_help": True,
    })
    repair: Dict[str, Any] = field(default_factory=lambda: {
        "currency": "GOLD",
        "use_gems": False,
    })
    display: Dict[str, Any] = field(default_factory=lambda: {
        "managed_by_game": True,
        "override_only_when_needed": True,
    })

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlayerProfile":
        profile = cls()
        for name in (
            "mode", "collection", "pet", "king",
            "upgrade", "repair", "display",
        ):
            if name in data:
                setattr(profile, name, data[name])
        return profile

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "collection": self.collection,
            "pet": self.pet,
            "king": self.king,
            "upgrade": self.upgrade,
            "repair": self.repair,
            "display": self.display,
        }
