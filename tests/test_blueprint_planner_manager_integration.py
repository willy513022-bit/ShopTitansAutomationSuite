from __future__ import annotations

from core.decision_context import DecisionContext
from core.scheduler import Scheduler
from models.game_item import GameItem
from planner.blueprint_candidate import BlueprintCandidate
from planners import (
    BlueprintCraftingPlanner,
    PlannerManager,
    ProductionPlanner,
)
from vision.blueprint_card_scanner import BlueprintCardState
from vision.blueprint_progress_models import ImageRegion


def make_blueprint_candidate() -> BlueprintCandidate:
    state = BlueprintCardState(
        row=1,
        column=2,
        card_region=ImageRegion(
            x=438,
            y=1273,
            width=207,
            height=250,
        ),
        item_name="Bleakspire Roots",
        current_progress=4,
        current_target=6,
        remaining=2,
        name_confidence=0.98,
        progress_confidence=0.88,
        name_match_score=1.0,
    )

    item = GameItem(
        item_id="herbal_medicine_bleakspire_roots",
        name="Bleakspire Roots",
        item_type="Herbal Medicine",
        tier=11,
        craft_time_seconds=39600,
    )

    return BlueprintCandidate(
        state=state,
        item=item,
    )


def make_context() -> DecisionContext:
    return DecisionContext(
        world_state={
            "production": {
                "free_slots": 2,
                "candidates": [
                    {
                        "item": "Squire Sword",
                        "current_stock": 5,
                        "target_stock": 20,
                    }
                ],
            },
            "blueprint": {
                "candidates": [
                    make_blueprint_candidate()
                ],
            },
        }
    )


def test_manager_accepts_craft_and_blueprint_planners():
    manager = PlannerManager(
        [
            ProductionPlanner(),
            BlueprintCraftingPlanner(),
        ]
    )

    assert [
        planner.name
        for planner in manager.planners
    ] == [
        "craft",
        "blueprint",
    ]


def test_manager_collects_both_decisions():
    manager = PlannerManager(
        [
            ProductionPlanner(),
            BlueprintCraftingPlanner(),
        ]
    )

    decisions = manager.collect(
        make_context()
    )

    assert len(decisions) == 2

    assert {
        decision.planner
        for decision in decisions
    } == {
        "craft",
        "blueprint",
    }

    assert all(
        decision.action == "CRAFT"
        for decision in decisions
    )


def test_blueprint_decision_preserves_runtime_payload():
    manager = PlannerManager(
        [
            BlueprintCraftingPlanner(),
        ]
    )

    decisions = manager.collect(
        make_context()
    )

    assert len(decisions) == 1

    decision = decisions[0]

    assert (
        decision.payload["target_item"]
        == "Bleakspire Roots"
    )

    assert (
        decision.payload["requested_count"]
        == 1
    )

    assert (
        decision.payload[
            "remaining_stage_crafts"
        ]
        == 2
    )

    assert (
        decision.payload["source"]
        == "blueprint_milestone"
    )


def test_scheduler_can_rank_blueprint_and_craft():
    manager = PlannerManager(
        [
            ProductionPlanner(),
            BlueprintCraftingPlanner(),
        ]
    )

    result = manager.select(
        make_context(),
        scheduler=Scheduler(),
    )

    assert result.has_winner

    assert len(result.ranked) == 2

    planner_names = {
        scored.decision.planner
        for scored in result.ranked
    }

    assert planner_names == {
        "craft",
        "blueprint",
    }


def test_blueprint_is_not_skipped_by_default_strategy():
    manager = PlannerManager(
        [
            BlueprintCraftingPlanner(),
        ]
    )

    result = manager.select(
        make_context()
    )

    assert result.has_winner
    assert result.winner is not None

    assert (
        result.winner.decision.planner
        == "blueprint"
    )

    assert result.skipped == ()


def test_blueprint_and_craft_have_distinct_planner_names():
    production = ProductionPlanner()
    blueprint = BlueprintCraftingPlanner()

    assert production.name == "craft"
    assert blueprint.name == "blueprint"
    assert production.name != blueprint.name