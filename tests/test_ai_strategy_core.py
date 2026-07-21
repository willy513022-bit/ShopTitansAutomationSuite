from ai.action import ActionType
from ai.game_state import (
    CollectionTask,
    CraftJob,
    CurrencyState,
    CustomerOffer,
    EnergyState,
    GameState,
    MarketOpportunity,
    QuestOption,
)
from ai.strategy_engine import StrategyEngine


def print_result(
    name: str,
    state: GameState,
    expected: ActionType,
) -> None:
    action = StrategyEngine().decide(
        state
    )

    print()
    print(name)
    print("-" * 70)
    print(
        "決策：",
        action.action_type.value,
    )
    print(
        "分數：",
        action.score,
    )
    print(
        "原因：",
        action.reason,
    )

    assert (
        action.action_type
        == expected
    ), (
        f"預期 {expected.value}，"
        f"實際 {action.action_type.value}"
    )


def main() -> None:
    print("AI Strategy Core 測試")
    print("=" * 70)

    print_result(
        "案例 1：低能量時優先閒談",
        GameState(
            energy=EnergyState(
                current=80,
                maximum=1000,
            ),
            customers=[
                CustomerOffer(
                    customer_id="c1",
                    item_id="sword_squire_sword",
                    item_name="Squire Sword",
                    item_value=1000,
                )
            ],
        ),
        ActionType.SMALL_TALK,
    )

    print_result(
        "案例 2：能量快滿，高價商品優先加價",
        GameState(
            energy=EnergyState(
                current=950,
                maximum=1000,
            ),
            customers=[
                CustomerOffer(
                    customer_id="c2",
                    item_id="spear_blackthorn_razor",
                    item_name="Blackthorn Razor",
                    item_value=1_650_000,
                )
            ],
        ),
        ActionType.SURCHARGE,
    )

    print_result(
        "案例 3：能量快滿但沒有客人，"
        "加速收藏製作",
        GameState(
            energy=EnergyState(
                current=980,
                maximum=1000,
            ),
            craft_jobs=[
                CraftJob(
                    job_id="j1",
                    item_id="sword_cutlass",
                    item_name="Cutlass",
                    remaining_seconds=900,
                    priority=100,
                    collection_related=True,
                    can_speed_up_with_energy=True,
                )
            ],
        ),
        ActionType.SPEED_UP_CRAFT,
    )

    print_result(
        "案例 4：收藏物品已可捐贈",
        GameState(
            collection_tasks=[
                CollectionTask(
                    task_id="t1",
                    item_id="spear_blackthorn_razor",
                    item_name="Blackthorn Razor",
                    target_quality="Legendary",
                    ready_to_donate=True,
                )
            ],
        ),
        ActionType.DONATE_COLLECTION,
    )

    print_result(
        "案例 5：缺冒險素材且隊伍為綠色笑臉",
        GameState(
            collection_tasks=[
                CollectionTask(
                    task_id="t2",
                    item_id="spear_blackthorn_razor",
                    item_name="Blackthorn Razor",
                    target_quality="Legendary",
                    missing_materials=[
                        "Spooky Ectoplasm"
                    ],
                )
            ],
            quest_options=[
                QuestOption(
                    quest_id="q1",
                    area_name="Haunted Castle",
                    material_name=(
                        "Spooky Ectoplasm"
                    ),
                    party_face_status=(
                        "GREEN_HAPPY"
                    ),
                )
            ],
        ),
        ActionType.START_QUEST,
    )

    print_result(
        "案例 6：黃色表情不可出發，"
        "改採市場低價購買",
        GameState(
            currencies=CurrencyState(
                gold=10_000_000
            ),
            collection_tasks=[
                CollectionTask(
                    task_id="t3",
                    item_id="sword_cutlass",
                    item_name="Cutlass",
                    target_quality="Epic",
                    missing_materials=[
                        "Silver Dust"
                    ],
                )
            ],
            quest_options=[
                QuestOption(
                    quest_id="q2",
                    area_name="Unknown",
                    material_name="Silver Dust",
                    party_face_status=(
                        "YELLOW_NEUTRAL"
                    ),
                )
            ],
            market_opportunities=[
                MarketOpportunity(
                    item_name="Silver Dust",
                    quantity_needed=2,
                    unit_price=5_000,
                    max_unit_price=8_000,
                )
            ],
        ),
        ActionType.BUY_MARKET,
    )

    print_result(
        "案例 7：收藏保留品不可出售",
        GameState(
            energy=EnergyState(
                current=900,
                maximum=1000,
            ),
            customers=[
                CustomerOffer(
                    customer_id="c3",
                    item_id="spear_blackthorn_razor",
                    item_name="Blackthorn Razor",
                    item_value=1_650_000,
                    reserved=True,
                    reservation_reason=(
                        "Legendary 收藏保留"
                    ),
                )
            ],
        ),
        ActionType.WAIT,
    )

    print()
    print("=" * 70)
    print("全部案例通過")


if __name__ == "__main__":
    main()
