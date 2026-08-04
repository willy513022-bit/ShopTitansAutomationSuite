from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping, Optional


class BlueprintProgressStatus(StrEnum):
    """
    藍圖里程碑目前狀態。
    """

    IN_PROGRESS = "in_progress"
    CURRENT_STAGE_COMPLETE = "current_stage_complete"
    ALL_MILESTONES_COMPLETE = "all_milestones_complete"
    UNKNOWN = "unknown"


class BlueprintPlanAction(StrEnum):
    """
    BlueprintPlanner 建議執行的動作。
    """

    CRAFT_CURRENT_STAGE = "craft_current_stage"
    RESCAN_PROGRESS = "rescan_progress"
    COLLECTION_READY = "collection_ready"
    WAIT_FOR_VALID_STATE = "wait_for_valid_state"


@dataclass(frozen=True, slots=True)
class BlueprintProgress:
    """
    從製作列表或藍圖畫面讀取到的目前里程碑進度。

    例如：
        current_progress=10
        current_target=15

    表示目前階段已製作 10 件，
    此階段目標為 15 件，還差 5 件。

    all_milestones_complete=True 時：
        current_progress 和 current_target 可以是 None。
    """

    item_name: str
    current_progress: Optional[int]
    current_target: Optional[int]
    completed_milestones: Optional[int] = None
    total_milestones: int = 5
    all_milestones_complete: bool = False
    confidence: float = 1.0
    source: str = "unknown"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        item_name = self.item_name.strip()

        if not item_name:
            raise ValueError("item_name is required")

        if self.total_milestones <= 0:
            raise ValueError(
                "total_milestones must be greater than 0"
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0 and 1"
            )

        if self.completed_milestones is not None:
            if self.completed_milestones < 0:
                raise ValueError(
                    "completed_milestones cannot be negative"
                )

            if self.completed_milestones > self.total_milestones:
                raise ValueError(
                    "completed_milestones cannot exceed "
                    "total_milestones"
                )

        if self.all_milestones_complete:
            if (
                self.completed_milestones is not None
                and self.completed_milestones
                != self.total_milestones
            ):
                raise ValueError(
                    "completed blueprint must have all "
                    "milestones completed"
                )
        else:
            if self.current_progress is None:
                raise ValueError(
                    "current_progress is required when "
                    "milestones are incomplete"
                )

            if self.current_target is None:
                raise ValueError(
                    "current_target is required when "
                    "milestones are incomplete"
                )

            if self.current_progress < 0:
                raise ValueError(
                    "current_progress cannot be negative"
                )

            if self.current_target <= 0:
                raise ValueError(
                    "current_target must be greater than 0"
                )

            if self.current_progress > self.current_target:
                raise ValueError(
                    "current_progress cannot exceed "
                    "current_target"
                )

        object.__setattr__(self, "item_name", item_name)
        object.__setattr__(
            self,
            "source",
            self.source.strip() or "unknown",
        )
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )

    @property
    def remaining_crafts(self) -> int:
        """
        目前里程碑還需要製作幾件。

        全里程碑完成時回傳 0。
        """

        if self.all_milestones_complete:
            return 0

        assert self.current_progress is not None
        assert self.current_target is not None

        return max(
            0,
            self.current_target - self.current_progress,
        )

    @property
    def current_stage_complete(self) -> bool:
        """
        畫面若顯示 current == target，
        表示目前里程碑已達成，但 UI 可能尚未刷新到下一階段。
        """

        if self.all_milestones_complete:
            return False

        return self.remaining_crafts == 0

    @property
    def status(self) -> BlueprintProgressStatus:
        if self.all_milestones_complete:
            return (
                BlueprintProgressStatus
                .ALL_MILESTONES_COMPLETE
            )

        if self.current_stage_complete:
            return (
                BlueprintProgressStatus
                .CURRENT_STAGE_COMPLETE
            )

        return BlueprintProgressStatus.IN_PROGRESS


@dataclass(frozen=True, slots=True)
class BlueprintPlan:
    """
    BlueprintPlanner 的純計算結果。
    """

    item_name: str
    action: BlueprintPlanAction
    current_progress: Optional[int]
    current_target: Optional[int]
    crafts_remaining: int
    collection_unlocked: bool
    should_rescan_after_execution: bool
    completed_milestones: Optional[int] = None
    total_milestones: int = 5
    reason: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        item_name = self.item_name.strip()
        reason = self.reason.strip()

        if not item_name:
            raise ValueError("item_name is required")

        if self.crafts_remaining < 0:
            raise ValueError(
                "crafts_remaining cannot be negative"
            )

        if self.total_milestones <= 0:
            raise ValueError(
                "total_milestones must be greater than 0"
            )

        if self.collection_unlocked:
            if self.crafts_remaining != 0:
                raise ValueError(
                    "collection-ready plan cannot require crafts"
                )

            if self.action is not BlueprintPlanAction.COLLECTION_READY:
                raise ValueError(
                    "collection_unlocked requires "
                    "COLLECTION_READY action"
                )

        if (
            self.action
            is BlueprintPlanAction.CRAFT_CURRENT_STAGE
            and self.crafts_remaining <= 0
        ):
            raise ValueError(
                "CRAFT_CURRENT_STAGE requires "
                "crafts_remaining > 0"
            )

        object.__setattr__(self, "item_name", item_name)
        object.__setattr__(self, "reason", reason)
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )

    @property
    def actionable(self) -> bool:
        return self.action in {
            BlueprintPlanAction.CRAFT_CURRENT_STAGE,
            BlueprintPlanAction.RESCAN_PROGRESS,
            BlueprintPlanAction.COLLECTION_READY,
        }

    @property
    def requires_crafting(self) -> bool:
        return (
            self.action
            is BlueprintPlanAction.CRAFT_CURRENT_STAGE
        )

    @property
    def waiting_for_rescan(self) -> bool:
        return (
            self.action
            is BlueprintPlanAction.RESCAN_PROGRESS
        )