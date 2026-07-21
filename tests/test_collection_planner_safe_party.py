from planner.collection_planner import (
    CollectionPlanner,
)
from planner.models import (
    AcquisitionMethod,
    CollectionTarget,
    MaterialNeed,
    QuestPartyCandidate,
)


def main() -> None:
    print("Collection Planner Safe Party 測試")
    print("=" * 72)

    target = CollectionTarget(
        task_id="task-blackthorn",
        item_id="spear_blackthorn_razor",
        item_name="Blackthorn Razor",
        target_quality="Legendary",
        priority=100,
        material_needs=(
            MaterialNeed(
                item_name="Spooky Ectoplasm",
                quantity=6,
                inventory_quantity=0,
                quest_area="Haunted Castle",
                quest_parties=(
                    QuestPartyCandidate(
                        party_id="party-yellow",
                        face_status="YELLOW_NEUTRAL",
                        estimated_success_score=75,
                    ),
                    QuestPartyCandidate(
                        party_id="party-green",
                        face_status="GREEN_HAPPY",
                        estimated_success_score=95,
                    ),
                ),
            ),
        ),
    )

    plan = CollectionPlanner().build_plan(
        targets=[target],
        current_gold=10_000_000,
        free_craft_slots=0,
    )

    assert plan.selected_step is not None
    assert (
        plan.selected_step.method
        == AcquisitionMethod.QUEST
    )
    assert (
        plan.selected_step.payload[
            "party_id"
        ]
        == "party-green"
    )

    print(
        "selected party：",
        plan.selected_step.payload[
            "party_id"
        ],
    )
    print(
        "face status：",
        plan.selected_step.payload[
            "face_status"
        ],
    )
    print("測試通過")


if __name__ == "__main__":
    main()
