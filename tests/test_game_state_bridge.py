from ai.action import ActionType
from ai.game_state import (
    CraftJob,
    CustomerOffer,
    MarketOpportunity,
    QuestOption,
)
from ai.strategy_engine import StrategyEngine
from inventory.manager import inventory_manager
from models.inventory import (
    InventoryItemKey,
    InventoryStack,
)
from models.quality import Quality
from state.collection_state_provider import (
    CollectionGoalConfig,
    CollectionStateProvider,
)
from state.craft_state_provider import (
    CraftQueueSnapshot,
    CraftStateProvider,
)
from state.currency_state_provider import (
    CurrencySnapshot,
    CurrencyStateProvider,
)
from state.customer_state_provider import (
    CustomerSnapshot,
    CustomerStateProvider,
)
from state.energy_state_provider import (
    EnergySnapshot,
    EnergyStateProvider,
)
from state.game_state_builder import (
    GameStateBuilder,
)
from state.inventory_state_provider import (
    InventoryStateProvider,
)
from state.market_state_provider import (
    MarketSnapshot,
    MarketStateProvider,
)
from state.quest_state_provider import (
    QuestSnapshot,
    QuestStateProvider,
)


def main() -> None:
    print("GameState Bridge 測試")
    print("=" * 70)

    inventory_manager.replace_snapshot(
        [
            InventoryStack(
                key=InventoryItemKey(
                    item_id="sword_squire_sword",
                    quality=Quality.NORMAL,
                ),
                item_name="Squire Sword",
                quantity=20,
            ),
            InventoryStack(
                key=InventoryItemKey(
                    item_id="sword_cutlass",
                    quality=Quality.NORMAL,
                ),
                item_name="Cutlass",
                quantity=2,
            ),
        ]
    )

    builder = GameStateBuilder(
        providers=[
            InventoryStateProvider(),
            EnergyStateProvider(
                EnergySnapshot(
                    current=950,
                    maximum=1000,
                )
            ),
            CurrencyStateProvider(
                CurrencySnapshot(
                    gold=10_000_000,
                    gems=500,
                )
            ),
            CollectionStateProvider(
                goals=[
                    CollectionGoalConfig(
                        task_id="collection-001",
                        item_id="spear_blackthorn_razor",
                        item_name="Blackthorn Razor",
                        target_quality=Quality.LEGENDARY,
                        missing_materials=(
                            "Spooky Ectoplasm",
                        ),
                        priority=90,
                    )
                ]
            ),
            CraftStateProvider(
                CraftQueueSnapshot(
                    jobs=(
                        CraftJob(
                            job_id="craft-001",
                            item_id="sword_cutlass",
                            item_name="Cutlass",
                            remaining_seconds=900,
                            priority=100,
                            collection_related=True,
                            can_speed_up_with_energy=True,
                        ),
                    ),
                    free_slots=0,
                )
            ),
            CustomerStateProvider(
                CustomerSnapshot(
                    offers=(
                        CustomerOffer(
                            customer_id="customer-001",
                            item_id="spear_blackthorn_razor",
                            item_name="Blackthorn Razor",
                            item_value=1_650_000,
                            can_surcharge=True,
                            reserved=False,
                        ),
                    )
                )
            ),
            QuestStateProvider(
                QuestSnapshot(
                    options=(
                        QuestOption(
                            quest_id="quest-001",
                            area_name="Haunted Castle",
                            material_name="Spooky Ectoplasm",
                            party_face_status="GREEN_HAPPY",
                        ),
                    )
                )
            ),
            MarketStateProvider(
                MarketSnapshot(
                    opportunities=(
                        MarketOpportunity(
                            item_name="Spooky Ectoplasm",
                            quantity_needed=6,
                            unit_price=10_000,
                            max_unit_price=15_000,
                        ),
                    )
                )
            ),
        ]
    )

    state = builder.build()

    print()
    print("Inventory Summary")
    print("-" * 70)
    summary = state.metadata[
        "inventory_summary"
    ]
    print("Stack：", summary.stack_count)
    print("總數量：", summary.total_quantity)

    print()
    print("State")
    print("-" * 70)
    print(
        "Energy：",
        state.energy.current,
        "/",
        state.energy.maximum,
    )
    print(
        "Gold：",
        state.currencies.gold,
    )
    print(
        "Collection Tasks：",
        len(state.collection_tasks),
    )
    print(
        "Craft Jobs：",
        len(state.craft_jobs),
    )
    print(
        "Customers：",
        len(state.customers),
    )
    print(
        "Quest Options：",
        len(state.quest_options),
    )
    print(
        "Market Opportunities：",
        len(state.market_opportunities),
    )

    action = StrategyEngine().decide(
        state
    )

    print()
    print("AI Decision")
    print("-" * 70)
    print("Action：", action.action_type.value)
    print("Score：", action.score)
    print("Reason：", action.reason)
    print("Payload：", action.payload)

    assert (
        action.action_type
        == ActionType.SURCHARGE
    )

    print()
    print("=" * 70)
    print("GameState Bridge 測試通過")


if __name__ == "__main__":
    main()
