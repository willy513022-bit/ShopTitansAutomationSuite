from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RewardClaimSession:
    claim_count: int = 0

    @property
    def expect_fullscreen_reward(self) -> bool:
        return self.claim_count == 0

    def record_claim(self) -> None:
        self.claim_count += 1

    def reopen(self) -> None:
        self.claim_count = 0
