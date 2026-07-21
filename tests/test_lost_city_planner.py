from events.lost_city.models import (
    BossQuestState,
    LostCityAction,
    LostCityBossQuest,
    LostCityMilestone,
    LostCityParty,
    LostCityRepeatableQuest,
    LostCityState,
)
from events.lost_city.planner import (
    LostCityPlanner,
    LostCityPolicy,
)


def main() -> None:
    print("Lost City Planner 測試")
    print("=" * 72)

    green = LostCityParty(
        party_id="green",
        face_status="GREEN_HAPPY",
        available=True,
        estimated_success_score=95,
    )

    yellow = LostCityParty(
        party_id="yellow",
        face_status="YELLOW_NEUTRAL",
        available=True,
        estimated_success_score=75,
    )

    reserved = LostCityParty(
        party_id="reserved",
        face_status="GREEN_HAPPY",
        available=True,
        reserved_for_collection=True,
        estimated_success_score=100,
    )

    planner = LostCityPlanner(
        LostCityPolicy(
            reserve_party_count=0,
        )
    )

    milestone_state = LostCityState(
        active=True,
        current_gold=10_000,
        event_seconds_remaining=7_200,
        milestones=(
            LostCityMilestone(
                milestone_id="m1",
                required_gold=8_000,
                reward_name="獎勵",
                claimable=True,
                claimed=False,
            ),
        ),
    )

    decision = planner.decide(
        milestone_state
    )

    print(
        "案例1：",
        decision.action.value,
    )

    assert (
        decision.action
        == LostCityAction.CLAIM_MILESTONE
    )

    boss_state = LostCityState(
        active=True,
        current_gold=0,
        event_seconds_remaining=7_200,
        boss_quests=(
            LostCityBossQuest(
                quest_id="boss1",
                name="Golden Golem",
                state=BossQuestState.AVAILABLE,
                expected_gold=5_000,
                expected_key_chance_score=90,
                parties=(
                    green,
                    reserved,
                ),
            ),
        ),
        repeatable_quests=(
            LostCityRepeatableQuest(
                quest_id="normal1",
                name="Golden Hall",
                expected_gold=1_000,
                duration_seconds=600,
                parties=(
                    green,
                    yellow,
                ),
            ),
        ),
    )

    decision = planner.decide(
        boss_state
    )

    print(
        "案例2：",
        decision.action.value,
    )

    assert (
        decision.action
        == LostCityAction.START_BOSS_QUEST
    )

    repeatable_state = LostCityState(
        active=True,
        current_gold=0,
        event_seconds_remaining=1_800,
        boss_quests=(
            LostCityBossQuest(
                quest_id="boss1",
                name="Golden Golem",
                state=(
                    BossQuestState
                    .COMPLETED_THIS_EVENT
                ),
                expected_gold=5_000,
                expected_key_chance_score=90,
                parties=(green,),
            ),
        ),
        repeatable_quests=(
            LostCityRepeatableQuest(
                quest_id="fast",
                name="Fast Route",
                expected_gold=1_000,
                duration_seconds=300,
                parties=(
                    green,
                    yellow,
                    reserved,
                ),
            ),
            LostCityRepeatableQuest(
                quest_id="slow",
                name="Slow Route",
                expected_gold=1_500,
                duration_seconds=900,
                parties=(
                    green,
                    yellow,
                ),
            ),
        ),
    )

    decision = planner.decide(
        repeatable_state
    )

    print(
        "案例3：",
        decision.action.value,
    )

    print(
        "選擇：",
        decision.payload,
    )

    assert (
        decision.action
        == LostCityAction.START_REPEATABLE_QUEST
    )

    assert (
        decision.payload["quest_id"]
        == "fast"
    )

    print("測試通過")


if __name__ == "__main__":
    main()
