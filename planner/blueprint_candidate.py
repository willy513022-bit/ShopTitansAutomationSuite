from __future__ import annotations

from dataclasses import dataclass

from models.game_item import GameItem
from vision.blueprint_card_scanner import (
    BlueprintCardState,
)


@dataclass(frozen=True, slots=True)
class BlueprintCandidate:
    """
    Blueprint 收藏候選項目。

    state:
        來自 Vision 的目前卡片狀態。

    item:
        來自 GameDataService 的正式 GameItem。

    Candidate 不複製 metadata，
    避免出現第二套 tier / craft_time / ingredient 資料。
    """

    state: BlueprintCardState
    item: GameItem

    def __post_init__(self) -> None:
        if not isinstance(
            self.state,
            BlueprintCardState,
        ):
            raise TypeError(
                "state must be BlueprintCardState"
            )

        if not isinstance(
            self.item,
            GameItem,
        ):
            raise TypeError(
                "item must be GameItem"
            )

        if not self.state.valid:
            raise ValueError(
                "candidate state must be valid"
            )

        if (
            self.state.item_name
            != self.item.name
        ):
            raise ValueError(
                "state item_name must match GameItem.name"
            )

    @property
    def remaining(self) -> int:
        assert self.state.remaining is not None
        return self.state.remaining

    @property
    def tier(self) -> int:
        return self.item.tier

    @property
    def craft_time_seconds(self) -> int:
        return self.item.craft_time_seconds

    @property
    def estimated_stage_time_seconds(self) -> int:
        """
        目前里程碑剩餘製作的基礎時間估計。

        第一版先用：

            remaining × craft_time_seconds

        尚未考慮：
        - 多製作槽並行
        - Energy 加速
        - Champion / worker bonus
        - 活動加速
        """

        return (
            self.remaining
            * self.craft_time_seconds
        )

    @property
    def item_name(self) -> str:
        return self.item.name