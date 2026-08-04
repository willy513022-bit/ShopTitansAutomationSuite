from __future__ import annotations

from planner.blueprint_models import (
    BlueprintPlan,
    BlueprintPlanAction,
    BlueprintProgress,
    BlueprintProgressStatus,
)


class BlueprintPlanner:
    """
    根據目前藍圖里程碑進度，
    決定是否需要繼續製作、重新掃描，
    或進入收藏流程。

    已確認的遊戲規則：

    1. 進度顯示為目前階段的 current / target。
    2. 完成一個里程碑後，進度會歸零。
    3. UI 會切換成下一個里程碑的 0 / N。
    4. 因此 Planner 每次只規劃目前階段。
    5. 完成目前階段後必須重新掃描，
       不可直接推測下一個里程碑目標。
    """

    def build_plan(
        self,
        progress: BlueprintProgress,
    ) -> BlueprintPlan:
        if not isinstance(progress, BlueprintProgress):
            raise TypeError(
                "progress must be BlueprintProgress"
            )

        if (
            progress.status
            is BlueprintProgressStatus
            .ALL_MILESTONES_COMPLETE
        ):
            return BlueprintPlan(
                item_name=progress.item_name,
                action=(
                    BlueprintPlanAction.COLLECTION_READY
                ),
                current_progress=None,
                current_target=None,
                crafts_remaining=0,
                collection_unlocked=True,
                should_rescan_after_execution=False,
                completed_milestones=(
                    progress.completed_milestones
                ),
                total_milestones=(
                    progress.total_milestones
                ),
                reason=(
                    "All blueprint milestones are complete; "
                    "the item can proceed to collection checks."
                ),
                metadata={
                    "source": progress.source,
                    "confidence": progress.confidence,
                },
            )

        if (
            progress.status
            is BlueprintProgressStatus
            .CURRENT_STAGE_COMPLETE
        ):
            return BlueprintPlan(
                item_name=progress.item_name,
                action=(
                    BlueprintPlanAction.RESCAN_PROGRESS
                ),
                current_progress=(
                    progress.current_progress
                ),
                current_target=(
                    progress.current_target
                ),
                crafts_remaining=0,
                collection_unlocked=False,
                should_rescan_after_execution=True,
                completed_milestones=(
                    progress.completed_milestones
                ),
                total_milestones=(
                    progress.total_milestones
                ),
                reason=(
                    "The current milestone target has been "
                    "reached. Wait for the game to refresh "
                    "and scan the next milestone progress."
                ),
                metadata={
                    "source": progress.source,
                    "confidence": progress.confidence,
                },
            )

        crafts_remaining = progress.remaining_crafts

        return BlueprintPlan(
            item_name=progress.item_name,
            action=(
                BlueprintPlanAction.CRAFT_CURRENT_STAGE
            ),
            current_progress=progress.current_progress,
            current_target=progress.current_target,
            crafts_remaining=crafts_remaining,
            collection_unlocked=False,
            should_rescan_after_execution=True,
            completed_milestones=(
                progress.completed_milestones
            ),
            total_milestones=(
                progress.total_milestones
            ),
            reason=(
                f"Current blueprint milestone is "
                f"{progress.current_progress}/"
                f"{progress.current_target}; "
                f"craft {crafts_remaining} more item(s), "
                "then rescan because the next milestone "
                "uses a new 0/N progress value."
            ),
            metadata={
                "source": progress.source,
                "confidence": progress.confidence,
                "current_stage_only": True,
            },
        )

    def build_from_values(
        self,
        *,
        item_name: str,
        current_progress: int | None,
        current_target: int | None,
        completed_milestones: int | None = None,
        total_milestones: int = 5,
        all_milestones_complete: bool = False,
        confidence: float = 1.0,
        source: str = "manual",
    ) -> BlueprintPlan:
        """
        方便 OCR Parser、範例與測試直接傳入數值。
        """

        progress = BlueprintProgress(
            item_name=item_name,
            current_progress=current_progress,
            current_target=current_target,
            completed_milestones=completed_milestones,
            total_milestones=total_milestones,
            all_milestones_complete=(
                all_milestones_complete
            ),
            confidence=confidence,
            source=source,
        )

        return self.build_plan(progress)