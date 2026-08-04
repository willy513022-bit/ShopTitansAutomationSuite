from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

from models.quality import Quality


def _normalize_quality_counts(
    values: Mapping[Quality, int],
) -> Mapping[Quality, int]:
    normalized: dict[Quality, int] = {}

    for quality, quantity in values.items():
        if not isinstance(quality, Quality):
            raise TypeError(
                "quality count keys must be Quality values"
            )

        normalized[quality] = max(0, int(quantity))

    return MappingProxyType(normalized)


@dataclass(frozen=True, slots=True)
class FusionStep:
    """
    一個品質融合步驟。

    output_quantity:
        預計產生多少件 target_quality。

    input_quantity:
        總共需要消耗多少件 source_quality。
    """

    source_quality: Quality
    target_quality: Quality
    input_per_output: int
    output_quantity: int

    def __post_init__(self) -> None:
        if self.input_per_output <= 0:
            raise ValueError(
                "input_per_output must be greater than 0"
            )

        if self.output_quantity < 0:
            raise ValueError(
                "output_quantity cannot be negative"
            )

    @property
    def input_quantity(self) -> int:
        return self.input_per_output * self.output_quantity


@dataclass(frozen=True, slots=True)
class FusionPlan:
    item_name: str

    # 收藏冊尚未登錄的品質。
    missing_qualities: frozenset[Quality]

    # 計算時讀到的現有庫存。
    inventory: Mapping[Quality, int]

    # 每一品質總共需要被消耗的數量。
    gross_demand: Mapping[Quality, int]

    # 扣除現有同品質庫存後，仍需產生的數量。
    production_shortfall: Mapping[Quality, int]

    # 實際需要執行的融合步驟。
    fusion_steps: tuple[FusionStep, ...]

    # 還需要直接製作多少件 Normal。
    normal_crafts_required: int

    # 預備幾次 Legendary 嘗試。
    legendary_attempts: int

    # 是否已經有 Legendary 可以直接捐獻。
    legendary_available_for_donation: bool

    notes: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        item_name = self.item_name.strip()

        if not item_name:
            raise ValueError("item_name is required")

        if self.legendary_attempts < 0:
            raise ValueError(
                "legendary_attempts cannot be negative"
            )

        object.__setattr__(self, "item_name", item_name)
        object.__setattr__(
            self,
            "missing_qualities",
            frozenset(self.missing_qualities),
        )
        object.__setattr__(
            self,
            "inventory",
            _normalize_quality_counts(self.inventory),
        )
        object.__setattr__(
            self,
            "gross_demand",
            _normalize_quality_counts(self.gross_demand),
        )
        object.__setattr__(
            self,
            "production_shortfall",
            _normalize_quality_counts(
                self.production_shortfall
            ),
        )
        object.__setattr__(
            self,
            "fusion_steps",
            tuple(self.fusion_steps),
        )
        object.__setattr__(
            self,
            "notes",
            tuple(self.notes),
        )

    @property
    def requires_work(self) -> bool:
        return bool(
            self.normal_crafts_required
            or self.fusion_steps
        )

    def demand_for(self, quality: Quality) -> int:
        return self.gross_demand.get(quality, 0)

    def shortfall_for(self, quality: Quality) -> int:
        return self.production_shortfall.get(quality, 0)

    def fusion_output_for(self, quality: Quality) -> int:
        return sum(
            step.output_quantity
            for step in self.fusion_steps
            if step.target_quality is quality
        )