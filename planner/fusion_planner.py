from __future__ import annotations

from collections.abc import Iterable, Mapping

from models.quality import Quality
from planner.fusion_models import FusionPlan, FusionStep
from planner.fusion_rules import (
    QUALITY_ORDER,
    fusion_requirement,
    previous_quality,
)


class FusionPlanner:
    """
    計算完成收藏所需的製作與融合數量。

    已確認的遊戲規則：

        Normal ×4     -> Superior ×1
        Superior ×5   -> Flawless ×1
        Flawless ×5   -> Epic ×1
        Epic ×5       -> Legendary 嘗試一次

    收藏登錄會消耗一件物品。

    Legendary 融合可能失敗，因此 Legendary 缺少時，
    legendary_attempts 代表要預備幾次嘗試所需的 Epic。
    """

    def build_plan(
        self,
        *,
        item_name: str,
        missing_qualities: Iterable[Quality],
        inventory: Mapping[Quality, int],
        legendary_attempts: int = 1,
    ) -> FusionPlan:
        name = item_name.strip()

        if not name:
            raise ValueError("item_name is required")

        missing = frozenset(missing_qualities)

        if Quality.UNKNOWN in missing:
            raise ValueError(
                "missing_qualities cannot contain UNKNOWN"
            )

        invalid_missing = {
            quality
            for quality in missing
            if not isinstance(quality, Quality)
        }

        if invalid_missing:
            raise TypeError(
                "missing_qualities must contain Quality values"
            )

        if legendary_attempts < 1:
            raise ValueError(
                "legendary_attempts must be at least 1"
            )

        normalized_inventory = {
            quality: max(
                0,
                int(inventory.get(quality, 0)),
            )
            for quality in QUALITY_ORDER
        }

        gross_demand = {
            quality: 0
            for quality in QUALITY_ORDER
        }

        shortfall = {
            quality: 0
            for quality in QUALITY_ORDER
        }

        notes: list[str] = []

        #
        # 先加入收藏登錄會消耗的物品。
        #

        for quality in missing:
            if quality is Quality.LEGENDARY:
                continue

            gross_demand[quality] += 1
            notes.append(
                f"Donate {quality.value}: "
                f"consume 1 {quality.value}"
            )

        #
        # Legendary 特殊處理。
        #

        legendary_missing = (
            Quality.LEGENDARY in missing
        )
        legendary_inventory = normalized_inventory[
            Quality.LEGENDARY
        ]

        legendary_available = bool(
            legendary_missing
            and legendary_inventory >= 1
        )

        if legendary_missing:
            if legendary_available:
                gross_demand[Quality.LEGENDARY] = 1

                notes.append(
                    "Legendary already exists in inventory; "
                    "reserve 1 for donation"
                )
            else:
                epic_for_attempts = (
                    legendary_attempts
                    * fusion_requirement(
                        Quality.LEGENDARY
                    )
                )

                gross_demand[Quality.EPIC] += (
                    epic_for_attempts
                )

                notes.append(
                    f"Prepare {legendary_attempts} "
                    "Legendary attempt(s): "
                    f"consume {epic_for_attempts} epic"
                )

        #
        # Legendary 現有物品只用來捐獻。
        # 不將 Legendary shortfall 視為可保證製造，
        # 因為融合可能失敗。
        #

        if gross_demand[Quality.LEGENDARY] > 0:
            available = normalized_inventory[
                Quality.LEGENDARY
            ]

            shortfall[Quality.LEGENDARY] = max(
                0,
                gross_demand[Quality.LEGENDARY]
                - available,
            )

        #
        # 從 Epic 一路往下展開需求。
        #

        fusion_steps_by_target: dict[
            Quality,
            FusionStep,
        ] = {}

        expandable_qualities = (
            Quality.EPIC,
            Quality.FLAWLESS,
            Quality.SUPERIOR,
        )

        for target_quality in expandable_qualities:
            available = normalized_inventory[
                target_quality
            ]

            required = gross_demand[target_quality]

            needed_output = max(
                0,
                required - available,
            )

            shortfall[target_quality] = needed_output

            if needed_output == 0:
                continue

            source_quality = previous_quality(
                target_quality
            )
            requirement = fusion_requirement(
                target_quality
            )

            source_needed = (
                needed_output * requirement
            )

            gross_demand[source_quality] += (
                source_needed
            )

            fusion_steps_by_target[target_quality] = (
                FusionStep(
                    source_quality=source_quality,
                    target_quality=target_quality,
                    input_per_output=requirement,
                    output_quantity=needed_output,
                )
            )

            notes.append(
                f"Produce {needed_output} "
                f"{target_quality.value}: "
                f"consume {source_needed} "
                f"{source_quality.value}"
            )

        #
        # Normal 無法再由更低品質融合取得，
        # 所以扣掉現有 Normal 後就是實際製作數。
        #

        normal_required = gross_demand[
            Quality.NORMAL
        ]
        normal_available = normalized_inventory[
            Quality.NORMAL
        ]

        normal_crafts_required = max(
            0,
            normal_required - normal_available,
        )

        shortfall[Quality.NORMAL] = (
            normal_crafts_required
        )

        if normal_crafts_required:
            notes.append(
                f"Craft {normal_crafts_required} normal"
            )

        #
        # 執行順序必須由低品質往高品質：
        # Normal -> Superior -> Flawless -> Epic。
        #

        ordered_steps = tuple(
            fusion_steps_by_target[quality]
            for quality in (
                Quality.SUPERIOR,
                Quality.FLAWLESS,
                Quality.EPIC,
            )
            if quality in fusion_steps_by_target
        )

        return FusionPlan(
            item_name=name,
            missing_qualities=missing,
            inventory=normalized_inventory,
            gross_demand=gross_demand,
            production_shortfall=shortfall,
            fusion_steps=ordered_steps,
            normal_crafts_required=normal_crafts_required,
            legendary_attempts=(
                legendary_attempts
                if legendary_missing
                and not legendary_available
                else 0
            ),
            legendary_available_for_donation=(
                legendary_available
            ),
            notes=tuple(notes),
        )