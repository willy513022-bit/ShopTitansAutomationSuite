import pytest

from models.quality import Quality
from planner.fusion_planner import FusionPlanner


def inventory(**quantities):
    result = {
        quality: 0
        for quality in (
            Quality.NORMAL,
            Quality.SUPERIOR,
            Quality.FLAWLESS,
            Quality.EPIC,
            Quality.LEGENDARY,
        )
    }

    for name, quantity in quantities.items():
        result[Quality(name)] = quantity

    return result


def test_luxurious_macuahuitl_one_legendary_attempt():
    plan = FusionPlanner().build_plan(
        item_name="Luxurious Macuahuitl",
        missing_qualities={
            Quality.FLAWLESS,
            Quality.EPIC,
            Quality.LEGENDARY,
        },
        inventory=inventory(
            superior=1,
        ),
        legendary_attempts=1,
    )

    # Flawless donation 1
    # Epic donation requires 5 Flawless
    # Legendary attempt requires 5 Epic = 25 Flawless
    # Total Flawless = 31
    assert plan.demand_for(Quality.FLAWLESS) == 31

    # 31 Flawless ×5 = 155 Superior.
    assert plan.demand_for(Quality.SUPERIOR) == 155

    # Existing Superior ×1, so produce 154 Superior.
    assert plan.shortfall_for(Quality.SUPERIOR) == 154

    # 154 Superior ×4 Normal.
    assert plan.normal_crafts_required == 616

    assert plan.fusion_output_for(
        Quality.FLAWLESS
    ) == 31

    assert plan.fusion_output_for(
        Quality.EPIC
    ) == 6

    assert plan.legendary_attempts == 1


def test_three_legendary_attempts_require_1616_normal():
    plan = FusionPlanner().build_plan(
        item_name="Luxurious Macuahuitl",
        missing_qualities={
            Quality.FLAWLESS,
            Quality.EPIC,
            Quality.LEGENDARY,
        },
        inventory=inventory(
            superior=1,
        ),
        legendary_attempts=3,
    )

    # Epic donation 1 + Legendary attempts 15.
    assert plan.demand_for(Quality.EPIC) == 16

    # Flawless donation 1 + 16 Epic ×5.
    assert plan.demand_for(Quality.FLAWLESS) == 81

    # 81 Flawless ×5 = 405 Superior.
    assert plan.demand_for(Quality.SUPERIOR) == 405

    # Existing Superior ×1 leaves 404.
    assert plan.shortfall_for(Quality.SUPERIOR) == 404

    assert plan.normal_crafts_required == 1616
    assert plan.legendary_attempts == 3


def test_existing_epic_reduces_lower_quality_need():
    plan = FusionPlanner().build_plan(
        item_name="Example Sword",
        missing_qualities={
            Quality.EPIC,
        },
        inventory=inventory(
            epic=1,
        ),
    )

    assert plan.normal_crafts_required == 0
    assert plan.fusion_steps == ()
    assert not plan.requires_work


def test_existing_legendary_can_be_donated_directly():
    plan = FusionPlanner().build_plan(
        item_name="Example Sword",
        missing_qualities={
            Quality.LEGENDARY,
        },
        inventory=inventory(
            legendary=1,
        ),
        legendary_attempts=5,
    )

    assert plan.legendary_available_for_donation
    assert plan.legendary_attempts == 0
    assert plan.normal_crafts_required == 0
    assert plan.demand_for(Quality.LEGENDARY) == 1


def test_missing_normal_collection_requires_one_normal():
    plan = FusionPlanner().build_plan(
        item_name="Example Sword",
        missing_qualities={
            Quality.NORMAL,
        },
        inventory=inventory(),
    )

    assert plan.normal_crafts_required == 1


def test_existing_normal_can_be_donated():
    plan = FusionPlanner().build_plan(
        item_name="Example Sword",
        missing_qualities={
            Quality.NORMAL,
        },
        inventory=inventory(
            normal=1,
        ),
    )

    assert plan.normal_crafts_required == 0


def test_invalid_legendary_attempts_rejected():
    with pytest.raises(ValueError):
        FusionPlanner().build_plan(
            item_name="Example Sword",
            missing_qualities={
                Quality.LEGENDARY,
            },
            inventory=inventory(),
            legendary_attempts=0,
        )


def test_unknown_quality_rejected():
    with pytest.raises(ValueError):
        FusionPlanner().build_plan(
            item_name="Example Sword",
            missing_qualities={
                Quality.UNKNOWN,
            },
            inventory=inventory(),
        )