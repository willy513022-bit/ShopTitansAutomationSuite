from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .profile import PlayerProfile


class SellDecision(str, Enum):
    ALLOW = "ALLOW"
    DENY_LEGENDARY = "DENY_LEGENDARY"
    DENY_COLLECTION_INCOMPLETE = "DENY_COLLECTION_INCOMPLETE"
    DENY_PERMANENT_KEEP = "DENY_PERMANENT_KEEP"


@dataclass(frozen=True)
class CollectionPolicy:
    profile: PlayerProfile

    def can_sell(
        self,
        *,
        item_name: str,
        quality: str,
        collection_complete: bool,
    ) -> SellDecision:
        quality_normalized = quality.strip().upper()
        permanent = {
            str(name).strip().casefold()
            for name in self.profile.collection.get("permanent_keep_items", [])
        }

        if item_name.strip().casefold() in permanent:
            return SellDecision.DENY_PERMANENT_KEEP

        if (
            quality_normalized == "LEGENDARY"
            and self.profile.collection.get("keep_legendary_forever", True)
        ):
            return SellDecision.DENY_LEGENDARY

        if (
            quality_normalized != "NORMAL"
            and not collection_complete
            and self.profile.collection.get(
                "keep_non_normal_until_collection_complete", True
            )
        ):
            return SellDecision.DENY_COLLECTION_INCOMPLETE

        return SellDecision.ALLOW
