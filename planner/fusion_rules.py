from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

from models.quality import Quality


# 產生 1 件目標品質，需要消耗多少件前一品質。
FUSION_INPUT_REQUIREMENTS: Mapping[Quality, int] = MappingProxyType(
    {
        Quality.SUPERIOR: 4,
        Quality.FLAWLESS: 5,
        Quality.EPIC: 5,
        Quality.LEGENDARY: 5,
    }
)


QUALITY_ORDER: tuple[Quality, ...] = (
    Quality.NORMAL,
    Quality.SUPERIOR,
    Quality.FLAWLESS,
    Quality.EPIC,
    Quality.LEGENDARY,
)


def previous_quality(quality: Quality) -> Quality:
    """回傳指定品質的前一階品質。"""

    try:
        index = QUALITY_ORDER.index(quality)
    except ValueError as exc:
        raise ValueError(
            f"Unsupported quality: {quality!r}"
        ) from exc

    if index == 0:
        raise ValueError(
            "Normal quality has no previous quality"
        )

    return QUALITY_ORDER[index - 1]


def fusion_requirement(target_quality: Quality) -> int:
    """取得融合出一件目標品質所需的前階物品數。"""

    if target_quality not in FUSION_INPUT_REQUIREMENTS:
        raise ValueError(
            f"Quality cannot be produced by fusion: "
            f"{target_quality.value}"
        )

    return FUSION_INPUT_REQUIREMENTS[target_quality]