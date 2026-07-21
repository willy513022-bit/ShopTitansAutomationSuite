from __future__ import annotations

from dataclasses import dataclass

from planner.models import QuestPartyCandidate


FACE_RISK_SCORE: dict[str, int] = {
    "GREEN_HAPPY": 100,
    "YELLOW_NEUTRAL": 70,
    "RED_UNHAPPY": 30,
    "PURPLE_TERRIFIED": 0,
    "UNKNOWN": -1,
}


@dataclass(frozen=True)
class QuestRiskPolicy:
    minimum_face_score: int = 70
    allow_unknown: bool = False

    def is_safe(
        self,
        party: QuestPartyCandidate,
    ) -> bool:
        if not party.available:
            return False

        score = FACE_RISK_SCORE.get(
            party.face_status,
            -1,
        )

        if score < 0 and not self.allow_unknown:
            return False

        return score >= self.minimum_face_score

    def choose_best_party(
        self,
        parties: tuple[QuestPartyCandidate, ...],
    ) -> QuestPartyCandidate | None:
        safe_parties = [
            party
            for party in parties
            if self.is_safe(party)
        ]

        if not safe_parties:
            return None

        return max(
            safe_parties,
            key=lambda party: (
                FACE_RISK_SCORE.get(
                    party.face_status,
                    -1,
                ),
                party.estimated_success_score,
            ),
        )
