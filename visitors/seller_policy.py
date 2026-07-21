from __future__ import annotations

from dataclasses import dataclass

from visitors.models import VisitorOffer, VisitorType


@dataclass(frozen=True)
class SellerDecision:
    should_buy: bool
    reason: str


class SellerPolicy:
    SELLER_TYPES = {
        VisitorType.CUSTOMER_SELLER,
        VisitorType.WORKER_SELLER,
    }

    def decide(
        self,
        offer: VisitorOffer,
        current_gold: int,
    ) -> SellerDecision:
        if offer.visitor_type not in self.SELLER_TYPES:
            return SellerDecision(
                should_buy=False,
                reason="不是客人或工人的出售事件",
            )

        if offer.gem_price not in {None, 0}:
            return SellerDecision(
                should_buy=False,
                reason="禁止使用鑽石購買",
            )

        if offer.gold_price is None:
            return SellerDecision(
                should_buy=False,
                reason="未辨識到金幣價格",
            )

        if current_gold < offer.gold_price:
            return SellerDecision(
                should_buy=False,
                reason="金幣不足",
            )

        return SellerDecision(
            should_buy=True,
            reason="客人／工人使用金幣出售物品，依策略一律買入",
        )
