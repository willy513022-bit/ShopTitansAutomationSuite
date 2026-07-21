from __future__ import annotations

from dataclasses import dataclass

from events.lost_city.models import (
    BossQuestState,
    LostCityAction,
    LostCityBossQuest,
    LostCityParty,
    LostCityRepeatableQuest,
    LostCityState,
)
from planner.quest_risk import FACE_RISK_SCORE


@dataclass(frozen=True)
class LostCityPolicy:
    minimum_face_score: int = 70
    reserve_party_count: int = 1
    prioritize_unfinished_bosses: bool = True
    prioritize_claimable_rewards: bool = True
    increase_priority_near_end_seconds: int = 3600


@dataclass(frozen=True)
class LostCityDecision:
    action: LostCityAction
    score: float
    reason: str
    payload: dict


class LostCityPlanner:
    def __init__(
        self,
        policy: LostCityPolicy | None = None,
    ) -> None:
        self.policy = policy or LostCityPolicy()

    def decide(
        self,
        state: LostCityState,
    ) -> LostCityDecision:
        if not state.active:
            return LostCityDecision(
                LostCityAction.WAIT_FOR_EVENT,
                0,
                "失落黃金城目前未開放",
                {},
            )

        claimable = [
            milestone
            for milestone in state.milestones
            if milestone.claimable
            and not milestone.claimed
        ]

        if (
            self.policy.prioritize_claimable_rewards
            and claimable
        ):
            target = min(
                claimable,
                key=lambda milestone: (
                    milestone.required_gold
                ),
            )

            return LostCityDecision(
                LostCityAction.CLAIM_MILESTONE,
                120,
                (
                    f"活動黃金已達 "
                    f"{target.required_gold}，"
                    f"可領取 {target.reward_name}"
                ),
                {
                    "milestone_id": (
                        target.milestone_id
                    )
                },
            )

        parties = self._available_parties(
            state
        )

        if not parties:
            return LostCityDecision(
                LostCityAction.WAIT_FOR_PARTY,
                10,
                "目前沒有符合安全門檻且未被保留的隊伍",
                {},
            )

        if self.policy.prioritize_unfinished_bosses:
            boss_decision = self._boss_decision(
                state.boss_quests,
                parties,
            )

            if boss_decision is not None:
                return boss_decision

        repeatable_decision = (
            self._repeatable_decision(
                state.repeatable_quests,
                parties,
                state.event_seconds_remaining,
            )
        )

        if repeatable_decision is not None:
            return repeatable_decision

        return LostCityDecision(
            LostCityAction.EVENT_COMPLETE,
            5,
            "目前沒有可執行的黃金城任務",
            {},
        )

    def _available_parties(
        self,
        state: LostCityState,
    ) -> list[LostCityParty]:
        unique: dict[str, LostCityParty] = {}

        for quest in (
            *state.boss_quests,
            *state.repeatable_quests,
        ):
            for party in quest.parties:
                unique[party.party_id] = party

        candidates = [
            party
            for party in unique.values()
            if party.available
            and not party.reserved_for_collection
            and not party.reserved_for_hero
            and FACE_RISK_SCORE.get(
                party.face_status,
                -1,
            )
            >= self.policy.minimum_face_score
        ]

        candidates.sort(
            key=lambda party: (
                FACE_RISK_SCORE.get(
                    party.face_status,
                    -1,
                ),
                party.estimated_success_score,
            ),
            reverse=True,
        )

        reserve_count = max(
            0,
            int(
                self.policy.reserve_party_count
            ),
        )

        # 重要修正：
        # Python 的 list[:-0] 會得到空清單，
        # 因此 reserve_party_count=0 時必須直接回傳。
        if reserve_count == 0:
            return candidates

        if len(candidates) <= reserve_count:
            return []

        return candidates[:-reserve_count]

    def _boss_decision(
        self,
        bosses: tuple[
            LostCityBossQuest,
            ...
        ],
        parties: list[LostCityParty],
    ) -> LostCityDecision | None:
        available_ids = {
            party.party_id
            for party in parties
        }

        candidates = []

        for boss in bosses:
            if boss.state != BossQuestState.AVAILABLE:
                continue

            safe_parties = [
                party
                for party in boss.parties
                if party.party_id
                in available_ids
            ]

            if not safe_parties:
                continue

            best_party = max(
                safe_parties,
                key=lambda party: (
                    FACE_RISK_SCORE.get(
                        party.face_status,
                        -1,
                    ),
                    party.estimated_success_score,
                ),
            )

            candidates.append(
                (
                    boss.expected_key_chance_score,
                    boss.expected_gold,
                    boss,
                    best_party,
                )
            )

        if not candidates:
            return None

        _, _, boss, party = max(
            candidates
        )

        return LostCityDecision(
            LostCityAction.START_BOSS_QUEST,
            110,
            (
                f"{boss.name} 尚未於本次活動完成，"
                "優先首通以提高寶箱鑰匙取得機會"
            ),
            {
                "quest_id": boss.quest_id,
                "party_id": party.party_id,
                "face_status": (
                    party.face_status
                ),
            },
        )

    def _repeatable_decision(
        self,
        quests: tuple[
            LostCityRepeatableQuest,
            ...
        ],
        parties: list[LostCityParty],
        event_seconds_remaining: int,
    ) -> LostCityDecision | None:
        available_ids = {
            party.party_id
            for party in parties
        }

        candidates = []

        for quest in quests:
            safe_parties = [
                party
                for party in quest.parties
                if party.party_id
                in available_ids
            ]

            if not safe_parties:
                continue

            best_party = max(
                safe_parties,
                key=lambda party: (
                    FACE_RISK_SCORE.get(
                        party.face_status,
                        -1,
                    ),
                    party.estimated_success_score,
                ),
            )

            efficiency = (
                quest.expected_gold
                / max(
                    quest.duration_seconds,
                    1,
                )
            )

            candidates.append(
                (
                    efficiency,
                    quest.expected_gold,
                    quest,
                    best_party,
                )
            )

        if not candidates:
            return None

        _, _, quest, party = max(
            candidates
        )

        score = 85

        if (
            event_seconds_remaining
            <= self.policy
            .increase_priority_near_end_seconds
        ):
            score += 15

        return LostCityDecision(
            LostCityAction.START_REPEATABLE_QUEST,
            score,
            (
                f"派遣 {party.party_id} "
                f"重複挑戰 {quest.name}，"
                "持續累積活動黃金"
            ),
            {
                "quest_id": quest.quest_id,
                "party_id": party.party_id,
                "face_status": (
                    party.face_status
                ),
                "expected_gold": (
                    quest.expected_gold
                ),
            },
        )
