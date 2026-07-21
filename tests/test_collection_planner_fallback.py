from planner.collection_planner import (
    CollectionPlanner,
)
from planner.models import (
    AcquisitionMethod,
    CollectionTarget,
    CollectionTaskStatus,
    MarketQuote,
    MaterialNeed,
    QuestPartyCandidate,
)


def main() -> None:
    print("Collection Planner Fallback 測試")
    print("=" * 72)

    blocked_target = CollectionTarget(
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
                        party_id="party-a",
                        face_status="RED_UNHAPPY",
                        estimated_success_score=50,
                    ),
                    QuestPartyCandidate(
                        party_id="party-b",
                        face_status="PURPLE_TERRIFIED",
                        estimated_success_score=20,
                    ),
                ),
                market_quote=None,
            ),
        ),
    )

    fallback_target = CollectionTarget(
        task_id="task-cutlass",
        item_id="sword_cutlass",
        item_name="Cutlass",
        target_quality="Epic",
        priority=90,
        material_needs=(
            MaterialNeed(
                item_name="Silver Dust",
                quantity=2,
                inventory_quantity=0,
                market_quote=MarketQuote(
                    item_name="Silver Dust",
                    unit_price=5_000,
                    quantity_available=10,
                    gold_only=True,
                ),
                max_unit_price=8_000,
            ),
        ),
    )

    plan = CollectionPlanner().build_plan(
        targets=[
            blocked_target,
            fallback_target,
        ],
        current_gold=10_000_000,
        free_craft_slots=0,
    )

    print()
    print("Task Status")
    print("-" * 72)

    for task_id, status in (
        plan.task_statuses.items()
    ):
        print(
            f"{task_id:<24} "
            f"{status.value}"
        )

    print()
    print("Blocked Reason")
    print("-" * 72)

    for task_id, reason in (
        plan.blocked_reasons.items()
    ):
        print(
            f"{task_id:<24} "
            f"{reason}"
        )

    print()
    print("Selected Step")
    print("-" * 72)

    assert plan.selected_step is not None

    print(
        "task：",
        plan.selected_step.task_id,
    )
    print(
        "method：",
        plan.selected_step.method.value,
    )
    print(
        "reason：",
        plan.selected_step.reason,
    )
    print(
        "payload：",
        plan.selected_step.payload,
    )

    assert (
        plan.task_statuses[
            "task-blackthorn"
        ]
        == CollectionTaskStatus
        .BLOCKED_NO_SAFE_PARTY
    )

    assert (
        plan.selected_task_id
        == "task-cutlass"
    )

    assert (
        plan.selected_step.method
        == AcquisitionMethod.MARKET
    )

    print()
    print("=" * 72)
    print(
        "測試通過："
        "高優先物品無安全隊伍時，"
        "已自動略過並處理下一項"
    )


if __name__ == "__main__":
    main()
