from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ActionType(str, Enum):
    WAIT = "wait"
    SMALL_TALK = "small_talk"
    DISCOUNT = "discount"
    NORMAL_SELL = "normal_sell"
    SURCHARGE = "surcharge"
    SPEED_UP_CRAFT = "speed_up_craft"
    START_CRAFT = "start_craft"
    START_FUSION = "start_fusion"
    DONATE_COLLECTION = "donate_collection"
    START_QUEST = "start_quest"
    CLAIM_QUEST = "claim_quest"
    BUY_MARKET = "buy_market"
    CLAIM_CRAFT = "claim_craft"


@dataclass(frozen=True)
class Action:
    action_type: ActionType
    score: float
    reason: str
    payload: dict[str, Any] = field(
        default_factory=dict
    )
