from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PaidOfferDecision:
    should_close: bool
    allow_purchase_click: bool
    reason: str


class PaidOfferPolicy:
    def decide(
        self,
        close_button_confidence: float,
        purchase_button_detected: bool,
        minimum_close_confidence: float = 0.90,
    ) -> PaidOfferDecision:
        if close_button_confidence >= minimum_close_confidence:
            return PaidOfferDecision(
                should_close=True,
                allow_purchase_click=False,
                reason="已高信心辨識關閉按鈕，只允許關閉彈窗",
            )

        return PaidOfferDecision(
            should_close=False,
            allow_purchase_click=False,
            reason=(
                "關閉按鈕辨識信心不足；"
                "不點擊任何付費或購買區域"
            ),
        )
