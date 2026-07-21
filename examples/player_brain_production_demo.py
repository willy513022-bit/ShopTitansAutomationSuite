from core.account_capabilities import AccountCapabilities
from core.player_profile import (
    CollectionPolicy,
    PlayerProfile,
    SafetyPolicy,
)
from core.production import ProductionMode, QueueObservation, SharedProductionQueue


def main() -> None:
    profile = PlayerProfile()
    collection = CollectionPolicy(profile)
    safety = SafetyPolicy(profile)
    capabilities = AccountCapabilities()

    queue = SharedProductionQueue(
        capabilities,
        QueueObservation(
            remaining_slots=5,
            ready_to_collect=2,
            mode=ProductionMode.CRAFT,
        ),
    )

    print("Player Brain + Shared Production Queue Demo")
    print("mode =", profile.mode)
    print("production_capacity =", queue.capacity)
    print("remaining_before_collect =", queue.remaining_slots)
    print("ready_to_collect =", queue.observation.ready_to_collect)
    print(
        "remaining_after_collect_2 =",
        queue.expected_remaining_after_collect(2),
    )
    print(
        "legendary_sell_decision =",
        collection.can_sell(
            item_name="Example Legendary",
            quality="Legendary",
            collection_complete=True,
        ).value,
    )
    print("may_use_upgrade_gems =", safety.may_use_gems("upgrade"))
    print("king_auto_sell =", safety.may_auto_sell_to_king())


if __name__ == "__main__":
    main()
