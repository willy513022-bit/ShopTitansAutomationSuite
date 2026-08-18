from __future__ import annotations

from datetime import datetime, timezone

from core.decision_context import DecisionContext
from models.game_item import GameItem
from navigation import (
    NavigationStateTracker,
    Navigator,
    Screen,
    TransitionAction,
    build_default_screen_graph,
)
from planner.blueprint_candidate import BlueprintCandidate
from planners.blueprint_crafting_planner import (
    BlueprintCraftingPlanner,
)
from runtime.craft_execution import (
    CraftExecutionPlanner,
    CraftExecutionStepKind,
)
from runtime.decision_bridge import RuntimeDecisionBridge
from runtime.decision_models import RuntimeDecisionKind
from vision.blueprint_card_scanner import BlueprintCardState
from vision.blueprint_progress_models import ImageRegion
from world_state.world_state import WorldState


def make_candidate() -> BlueprintCandidate:
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


def make_decision():
    context = DecisionContext(
        world_state={
            "production": {
                "free_slots": 2,
            },
            "blueprint": {
                "candidates": [
                    make_candidate(),
                ],
            },
        }
    )

    decision = (
        BlueprintCraftingPlanner()
        .evaluate(context)
    )

    assert decision is not None

    return decision


def make_world_state() -> WorldState:
    return WorldState(
        observed_at=datetime.now(
            timezone.utc
        )
    )


def test_blueprint_decision_reaches_runtime_bridge():
    decision = make_decision()

    runtime_decision = (
        RuntimeDecisionBridge()
        .decide(
            make_world_state(),
            decision,
        )
    )

    assert (
        runtime_decision.kind
        is RuntimeDecisionKind.DELEGATE_PLANNER
    )

    assert (
        runtime_decision.planner_decision
        is decision
    )


def test_runtime_decision_preserves_craft_payload():
    decision = make_decision()

    runtime_decision = (
        RuntimeDecisionBridge()
        .decide(
            make_world_state(),
            decision,
        )
    )

    planner_decision = (
        runtime_decision.planner_decision
    )

    assert planner_decision is not None

    assert planner_decision.action == "CRAFT"

    assert (
        planner_decision.payload["target_item"]
        == "Bleakspire Roots"
    )

    assert (
        planner_decision.payload["requested_count"]
        == 1
    )


def test_runtime_craft_plan_from_shop():
    decision = make_decision()

    runtime_decision = (
        RuntimeDecisionBridge()
        .decide(
            make_world_state(),
            decision,
        )
    )

    planner_decision = (
        runtime_decision.planner_decision
    )

    assert planner_decision is not None

    tracker = NavigationStateTracker()

    tracker.update(
        Screen.SHOP,
        0.99,
    )

    navigator = Navigator(
        build_default_screen_graph(),
        tracker,
    )

    craft_planner = CraftExecutionPlanner(
        navigator
    )

    plan = craft_planner.plan(
        planner_decision
    )

    assert plan.target_item == "Bleakspire Roots"
    assert plan.requested_count == 1

    assert plan.navigation.screens() == (
        Screen.SHOP,
        Screen.CRAFT,
    )
    assert len(
    plan.navigation.transitions
    ) == 1

    assert (
        plan.navigation.transitions[0].action
        is TransitionAction.OPEN_CRAFT
    )


def test_runtime_craft_plan_contains_safe_steps():
    decision = make_decision()

    tracker = NavigationStateTracker()
    tracker.update(
        Screen.SHOP,
        0.99,
    )

    plan = CraftExecutionPlanner(
        Navigator(
            build_default_screen_graph(),
            tracker,
        )
    ).plan(decision)

    kinds = tuple(
        step.kind
        for step in plan.steps
    )

    assert kinds == (
        CraftExecutionStepKind.NAVIGATE,
        CraftExecutionStepKind.FIND_ITEM,
        CraftExecutionStepKind.SELECT_ITEM,
        CraftExecutionStepKind.START_CRAFT,
        CraftExecutionStepKind.VERIFY_CRAFT_STARTED,
    )


def test_blueprint_plan_never_requests_remaining_all_at_once():
    decision = make_decision()

    assert (
        decision.payload[
            "remaining_stage_crafts"
        ]
        == 2
    )

    assert (
        decision.payload[
            "requested_count"
        ]
        == 1
    )


def test_already_on_craft_skips_navigation():
    decision = make_decision()

    tracker = NavigationStateTracker()
    tracker.update(
        Screen.CRAFT,
        0.99,
    )

    plan = CraftExecutionPlanner(
        Navigator(
            build_default_screen_graph(),
            tracker,
        )
    ).plan(decision)

    assert plan.navigation.is_noop

    assert (
        plan.steps[0].kind
        is CraftExecutionStepKind.FIND_ITEM
    )