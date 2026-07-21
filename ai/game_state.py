from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EnergyState:
    current: int = 0
    maximum: int = 1

    @property
    def ratio(self) -> float:
        if self.maximum <= 0:
            return 0.0

        return max(
            0.0,
            min(
                1.0,
                self.current / self.maximum,
            ),
        )


@dataclass
class CurrencyState:
    gold: int = 0
    gems: int = 0
    special_currency: dict[str, int] = field(
        default_factory=dict
    )


@dataclass
class CustomerOffer:
    customer_id: str
    item_id: str
    item_name: str
    item_value: int
    quantity: int = 1
    can_small_talk: bool = True
    can_discount: bool = True
    can_surcharge: bool = True
    reserved: bool = False
    reservation_reason: str | None = None


@dataclass
class CraftJob:
    job_id: str
    item_id: str
    item_name: str
    remaining_seconds: int
    priority: int = 0
    collection_related: bool = False
    can_speed_up_with_energy: bool = False


@dataclass
class QuestOption:
    quest_id: str
    area_name: str
    material_name: str
    party_face_status: str
    ready: bool = True
    expected_seconds: int = 0


@dataclass
class CollectionTask:
    task_id: str
    item_id: str
    item_name: str
    target_quality: str
    ready_to_donate: bool = False
    ready_to_fuse: bool = False
    ready_to_craft: bool = False
    missing_materials: list[str] = field(
        default_factory=list
    )
    priority: int = 90


@dataclass
class MarketOpportunity:
    item_name: str
    quantity_needed: int
    unit_price: int
    max_unit_price: int
    gold_only: bool = True

    @property
    def affordable_by_policy(self) -> bool:
        return (
            self.gold_only
            and self.unit_price
            <= self.max_unit_price
        )


@dataclass
class GameState:
    energy: EnergyState = field(
        default_factory=EnergyState
    )
    currencies: CurrencyState = field(
        default_factory=CurrencyState
    )
    customers: list[CustomerOffer] = field(
        default_factory=list
    )
    craft_jobs: list[CraftJob] = field(
        default_factory=list
    )
    collection_tasks: list[
        CollectionTask
    ] = field(
        default_factory=list
    )
    quest_options: list[QuestOption] = field(
        default_factory=list
    )
    market_opportunities: list[
        MarketOpportunity
    ] = field(
        default_factory=list
    )
    free_craft_slots: int = 0
    completed_quest_ids: list[str] = field(
        default_factory=list
    )
    completed_craft_job_ids: list[str] = field(
        default_factory=list
    )
    metadata: dict[str, Any] = field(
        default_factory=dict
    )
