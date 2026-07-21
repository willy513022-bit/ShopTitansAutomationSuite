from overlays.paid_offer_policy import PaidOfferPolicy


def main() -> None:
    print("Paid Offer Policy 測試")
    print("=" * 72)

    decision = PaidOfferPolicy().decide(
        close_button_confidence=0.97,
        purchase_button_detected=True,
    )

    print("should_close：", decision.should_close)
    print("allow_purchase_click：", decision.allow_purchase_click)
    print("reason：", decision.reason)

    assert decision.should_close is True
    assert decision.allow_purchase_click is False

    print("測試通過")


if __name__ == "__main__":
    main()
