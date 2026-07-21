from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class HeroRequestAction(str, Enum):
    SELL_TO_HERO = "sell_to_hero"
    CRAFT_FOR_HERO = "craft_for_hero"
    BUY_MARKET_FOR_HERO = "buy_market_for_hero"
    FREE_INVENTORY_SPACE = "free_inventory_space"
    WAIT = "wait"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class HeroRequestInput:
    item_id: str
    item_name: str
    quantity_needed: int
    inventory_quantity: int
    reserved_quantity: int
    craftable_now: bool
    market_available: bool
    market_unit_price: int | None
    max_market_unit_price: int | None
    inventory_full: bool
    current_gold: int


@dataclass(frozen=True)
class HeroRequestDecision:
    action: HeroRequestAction
    reason: str


class HeroRequestPlanner:
    def decide(
        self,
        request: HeroRequestInput,
    ) -> HeroRequestDecision:
        sellable_quantity = max(
            0,
            request.inventory_quantity
            - request.reserved_quantity,
        )

        if sellable_quantity >= request.quantity_needed:
            return HeroRequestDecision(
                HeroRequestAction.SELL_TO_HERO,
                "庫存足夠且不會動用收藏／前置保留量",
            )

        if request.craftable_now:
            return HeroRequestDecision(
                HeroRequestAction.CRAFT_FOR_HERO,
                "庫存不足，但可立即製作英雄需求物品",
            )

        if request.market_available:
            if request.inventory_full:
                return HeroRequestDecision(
                    HeroRequestAction.FREE_INVENTORY_SPACE,
                    "市場可買，但庫存已滿；先安全清出空間",
                )

            if (
                request.market_unit_price is not None
                and request.max_market_unit_price is not None
                and request.market_unit_price
                <= request.max_market_unit_price
                and request.current_gold
                >= request.market_unit_price
                * request.quantity_needed
            ):
                return HeroRequestDecision(
                    HeroRequestAction.BUY_MARKET_FOR_HERO,
                    "市場價格符合上限，使用金幣補足英雄需求",
                )

        return HeroRequestDecision(
            HeroRequestAction.BLOCKED,
            "目前無法安全取得英雄需求物品",
        )
