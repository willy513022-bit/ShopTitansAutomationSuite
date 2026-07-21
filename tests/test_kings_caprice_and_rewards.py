from events.kings_caprice_planner import (
    KingsCapricePlanner,
)
from events.models import EventCraftOption
from events.reward_claim_session import (
    RewardClaimSession,
)


def main() -> None:
    print("King's Caprice / Reward Session 測試")
    print("=" * 72)

    options = [
        EventCraftOption(
            item_id="a",
            item_name="Blocked Item",
            points=100,
            craft_time_seconds=10,
            resources_available=False,
        ),
        EventCraftOption(
            item_id="b",
            item_name="Fast Item",
            points=80,
            craft_time_seconds=20,
            resources_available=True,
        ),
        EventCraftOption(
            item_id="c",
            item_name="Slow Item",
            points=150,
            craft_time_seconds=100,
            resources_available=True,
        ),
    ]

    decision = KingsCapricePlanner().choose(
        options
    )

    print(
        "selected：",
        decision.selected_item_id,
    )
    print(
        "reason：",
        decision.reason,
    )

    assert decision.selected_item_id == "b"

    session = RewardClaimSession()

    print(
        "first expects fullscreen：",
        session.expect_fullscreen_reward,
    )
    assert session.expect_fullscreen_reward is True

    session.record_claim()

    print(
        "second expects fullscreen：",
        session.expect_fullscreen_reward,
    )
    assert session.expect_fullscreen_reward is False

    session.reopen()

    print(
        "reopen expects fullscreen：",
        session.expect_fullscreen_reward,
    )
    assert session.expect_fullscreen_reward is True

    print("測試通過")


if __name__ == "__main__":
    main()
