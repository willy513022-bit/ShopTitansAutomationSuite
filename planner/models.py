from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CollectionTaskStatus(str, Enum):
    READY = "ready"
    WAITING_CRAFT = "waiting_craft"
    WAITING_FUSION = "waiting_fusion"
    WAITING_QUEST = "waiting_quest"
    WAITING_MARKET = "waiting_market"
    READY_TO_DONATE = "ready_to_donate"
    BLOCKED_NO_SAFE_PARTY = "blocked_no_safe_party"
    BLOCKED_MARKET_PRICE = "blocked_market_price"
    BLOCKED_RESOURCE = "blocked_resource"
    COMPLETED = "completed"


class AcquisitionMethod(str, Enum):
    INVENTORY = "inventory"
    CRAFT = "craft"
    FUSION = "fusion"
    QUEST = "quest"
    MARKET = "market"
    WAIT = "wait"
    SKIP = "skip"
    DONATE = "donate"


@dataclass(frozen=True)
class QuestPartyCandidate:
    party_id: str
    face_status: str
    available: bool = True
    estimated_success_score: int = 0


@dataclass(frozen=True)
class MarketQuote:
    item_name: str
    unit_price: int
    quantity_available: int
    gold_only: bool = True


@dataclass(frozen=True)
class MaterialNeed:
    item_name: str
    quantity: int
    inventory_quantity: int = 0
    quest_area: str | None = None
    quest_parties: tuple[QuestPartyCandidate, ...] = field(
        default_factory=tuple
    )
    market_quote: MarketQuote | None = None
    max_unit_price: int | None = None


@dataclass(frozen=True)
class CollectionTarget:
    task_id: str
    item_id: str
    item_name: str
    target_quality: str
    priority: int = 90
    completed: bool = False
    ready_to_donate: bool = False
    ready_to_fuse: bool = False
    ready_to_craft: bool = False
    material_needs: tuple[MaterialNeed, ...] = field(
        default_factory=tuple
    )


@dataclass(frozen=True)
class PlannedStep:
    method: AcquisitionMethod
    task_id: str
    score: float
    reason: str
    payload: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class CollectionPlan:
    selected_task_id: str | None
    selected_step: PlannedStep | None
    task_statuses: dict[str, CollectionTaskStatus]
    blocked_reasons: dict[str, str]
    ranked_steps: tuple[PlannedStep, ...]
