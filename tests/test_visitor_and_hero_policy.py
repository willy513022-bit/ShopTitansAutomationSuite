from visitors.hero_request_planner import (
    HeroRequestAction,
    HeroRequestInput,
    HeroRequestPlanner,
)
from visitors.models import (
    VisitorIntent,
    VisitorOffer,
    VisitorType,
)
from visitors.seller_policy import SellerPolicy


def main() -> None:
    print("Visitor / Hero Policy 測試")
    print("=" * 72)

    worker_offer = VisitorOffer(
        visitor_id="worker-1",
        visitor_type=VisitorType.WORKER_SELLER,
        intent=VisitorIntent.SELL_ITEM_TO_PLAYER,
        item_id="sword_cutlass",
        item_name="Cutlass",
        gold_price=10000,
    )

    worker_decision = SellerPolicy().decide(
        worker_offer,
        current_gold=500000,
    )

    print(
        "worker should_buy：",
        worker_decision.should_buy,
    )

    assert worker_decision.should_buy is True

    hero_request = HeroRequestInput(
        item_id="sword_cutlass",
        item_name="Cutlass",
        quantity_needed=2,
        inventory_quantity=0,
        reserved_quantity=0,
        craftable_now=False,
        market_available=True,
        market_unit_price=5000,
        max_market_unit_price=8000,
        inventory_full=True,
        current_gold=1000000,
    )

    hero_decision = HeroRequestPlanner().decide(
        hero_request
    )

    print(
        "hero action：",
        hero_decision.action.value,
    )
    print(
        "hero reason：",
        hero_decision.reason,
    )

    assert (
        hero_decision.action
        == HeroRequestAction.FREE_INVENTORY_SPACE
    )

    print("測試通過")


if __name__ == "__main__":
    main()
