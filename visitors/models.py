from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class VisitorType(str, Enum):
    NORMAL_CUSTOMER = "normal_customer"
    CUSTOMER_SELLER = "customer_seller"
    WORKER_SELLER = "worker_seller"
    HERO_BUYER = "hero_buyer"
    EVENT_VISITOR = "event_visitor"
    BROWSER = "browser"
    UNKNOWN = "unknown"


class VisitorIntent(str, Enum):
    BUY_ITEM_FROM_PLAYER = "buy_item_from_player"
    SELL_ITEM_TO_PLAYER = "sell_item_to_player"
    SMALL_TALK = "small_talk"
    BROWSE = "browse"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class VisitorOffer:
    visitor_id: str
    visitor_type: VisitorType
    intent: VisitorIntent
    item_id: str | None
    item_name: str | None
    quantity: int = 1
    gold_price: int | None = None
    gem_price: int | None = None
