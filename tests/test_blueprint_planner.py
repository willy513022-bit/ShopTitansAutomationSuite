import pytest

from planner.blueprint_models import (
    BlueprintPlanAction,
    BlueprintProgress,
    BlueprintProgressStatus,
)
from planner.blueprint_planner import BlueprintPlanner


def test_progress_10_of_15_requires_five_crafts():
    progress = BlueprintProgress(
        item_name="Roland's Own",
        current_progress=10,
        current_target=15,
        completed_milestones=3,
        total_milestones=5,
        source="fixture",
    )

    assert progress.remaining_crafts == 5
    assert (
        progress.status
        is BlueprintProgressStatus.IN_PROGRESS
    )

    plan = BlueprintPlanner().build_plan(progress)

    assert (
        plan.action
        is BlueprintPlanAction.CRAFT_CURRENT_STAGE
    )
    assert plan.crafts_remaining == 5
    assert not plan.collection_unlocked
    assert plan.should_rescan_after_execution
    assert plan.requires_crafting


def test_progress_zero_of_seven_requires_seven_crafts():
    plan = BlueprintPlanner().build_from_values(
        item_name="Sandcastle Protector",
        current_progress=0,
        current_target=7,
        completed_milestones=0,
        source="fixture",
    )

    assert plan.crafts_remaining == 7
    assert (
        plan.action
        is BlueprintPlanAction.CRAFT_CURRENT_STAGE
    )


def test_progress_fourteen_of_fifteen_requires_one():
    plan = BlueprintPlanner().build_from_values(
        item_name="Example Blueprint",
        current_progress=14,
        current_target=15,
        completed_milestones=3,
    )

    assert plan.crafts_remaining == 1


def test_current_stage_complete_requires_rescan():
    progress = BlueprintProgress(
        item_name="Example Blueprint",
        current_progress=15,
        current_target=15,
        completed_milestones=3,
        source="fixture",
    )

    assert progress.current_stage_complete
    assert (
        progress.status
        is BlueprintProgressStatus
        .CURRENT_STAGE_COMPLETE
    )

    plan = BlueprintPlanner().build_plan(progress)

    assert (
        plan.action
        is BlueprintPlanAction.RESCAN_PROGRESS
    )
    assert plan.crafts_remaining == 0
    assert not plan.collection_unlocked
    assert plan.should_rescan_after_execution
    assert plan.waiting_for_rescan


def test_all_milestones_complete_unlocks_collection():
    progress = BlueprintProgress(
        item_name="Completed Blueprint",
        current_progress=None,
        current_target=None,
        completed_milestones=5,
        total_milestones=5,
        all_milestones_complete=True,
        source="fixture",
    )

    assert (
        progress.status
        is BlueprintProgressStatus
        .ALL_MILESTONES_COMPLETE
    )
    assert progress.remaining_crafts == 0

    plan = BlueprintPlanner().build_plan(progress)

    assert (
        plan.action
        is BlueprintPlanAction.COLLECTION_READY
    )
    assert plan.collection_unlocked
    assert plan.crafts_remaining == 0
    assert not plan.should_rescan_after_execution


def test_planner_only_handles_current_stage():
    plan = BlueprintPlanner().build_from_values(
        item_name="Example Blueprint",
        current_progress=10,
        current_target=15,
        completed_milestones=3,
    )

    # Planner 不會猜測下一階段是 25，
    # 也不會把後續門檻加進這次需求。
    assert plan.crafts_remaining == 5
    assert plan.metadata["current_stage_only"] is True


def test_negative_progress_rejected():
    with pytest.raises(ValueError):
        BlueprintProgress(
            item_name="Invalid",
            current_progress=-1,
            current_target=7,
        )


def test_zero_target_rejected():
    with pytest.raises(ValueError):
        BlueprintProgress(
            item_name="Invalid",
            current_progress=0,
            current_target=0,
        )


def test_progress_above_target_rejected():
    with pytest.raises(ValueError):
        BlueprintProgress(
            item_name="Invalid",
            current_progress=8,
            current_target=7,
        )


def test_missing_progress_rejected_when_incomplete():
    with pytest.raises(ValueError):
        BlueprintProgress(
            item_name="Invalid",
            current_progress=None,
            current_target=7,
        )


def test_completed_milestones_cannot_exceed_total():
    with pytest.raises(ValueError):
        BlueprintProgress(
            item_name="Invalid",
            current_progress=1,
            current_target=7,
            completed_milestones=6,
            total_milestones=5,
        )


def test_completed_blueprint_requires_all_stages():
    with pytest.raises(ValueError):
        BlueprintProgress(
            item_name="Invalid",
            current_progress=None,
            current_target=None,
            completed_milestones=4,
            total_milestones=5,
            all_milestones_complete=True,
        )


def test_build_plan_rejects_unknown_object():
    with pytest.raises(TypeError):
        BlueprintPlanner().build_plan(object())