from models.quality import Quality
from state.reservation_bridge import (
    ReservationBook,
)


def main() -> None:
    print("Reservation Bridge 測試")
    print("=" * 70)

    book = ReservationBook()

    book.reserve(
        item_id="spear_blackthorn_razor",
        quality=Quality.LEGENDARY,
        quantity=1,
        reason="收藏冊缺少 Legendary",
    )

    can_sell_one = book.can_sell(
        item_id="spear_blackthorn_razor",
        quality=Quality.LEGENDARY,
        current_quantity=1,
        requested_quantity=1,
    )

    can_sell_extra = book.can_sell(
        item_id="spear_blackthorn_razor",
        quality=Quality.LEGENDARY,
        current_quantity=2,
        requested_quantity=1,
    )

    print(
        "只有 1 件時可出售：",
        can_sell_one,
    )

    print(
        "有 2 件時可出售 1 件：",
        can_sell_extra,
    )

    assert can_sell_one is False
    assert can_sell_extra is True

    print("測試通過")


if __name__ == "__main__":
    main()
