from __future__ import annotations

from dataclasses import dataclass

from .profile import PlayerProfile


@dataclass(frozen=True)
class SafetyPolicy:
    profile: PlayerProfile

    def may_use_gems(self, purpose: str) -> bool:
        purpose = purpose.strip().lower()
        if purpose == "upgrade":
            return bool(self.profile.upgrade.get("use_gems", False))
        if purpose == "repair":
            return bool(self.profile.repair.get("use_gems", False))
        return False

    def repair_currency(self) -> str:
        return str(self.profile.repair.get("currency", "GOLD")).upper()

    def may_auto_sell_to_king(self) -> bool:
        return bool(self.profile.king.get("auto_sell", False))
