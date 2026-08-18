from __future__ import annotations

import unittest

from core.decision_context import DecisionContext
from models.game_item import GameItem
from planner.blueprint_candidate import BlueprintCandidate
from planners.blueprint_crafting_planner import (
    BlueprintCraftingPlanner,
)
from vision.blueprint_card_scanner import BlueprintCardState
from vision.blueprint_progress_models import ImageRegion


def make_candidate(
    *,
    name: str,
    tier: int,
    craft_time_seconds: int,
    current_progress: int,
    current_target: int,
    row: int = 0,
    column: int = 0,
) -> BlueprintCandidate:
    remaining = current_target - current_progress

    state = BlueprintCardState(
        row=row,
        column=column,
        card_region=ImageRegion(
            x=0,
            y=0,
            width=100,
            height=100,
        ),
        item_name=name,
        current_progress=current_progress,
        current_target=current_target,
        remaining=remaining,
        name_confidence=0.95,
        progress_confidence=0.95,
        name_match_score=0.99,
    )

    item = GameItem(
        item_id=name.lower().replace(" ", "_"),
        name=name,
        item_type="Test",
        tier=tier,
        craft_time_seconds=craft_time_seconds,
    )

    return BlueprintCandidate(
        state=state,
        item=item,
    )


class BlueprintCraftingPlannerTests(
    unittest.TestCase
):
    def setUp(self) -> None:
        self.planner = BlueprintCraftingPlanner()

    def test_returns_none_without_blueprint_snapshot(
        self,
    ) -> None:
        context = DecisionContext(
            world_state={
                "production": {
                    "free_slots": 2,
                }
            }
        )

        self.assertIsNone(
            self.planner.evaluate(context)
        )

    def test_returns_none_without_free_slots(
        self,
    ) -> None:
        candidate = make_candidate(
            name="Bleakspire Roots",
            tier=11,
            craft_time_seconds=39600,
            current_progress=4,
            current_target=6,
        )

        context = DecisionContext(
            world_state={
                "production": {
                    "free_slots": 0,
                },
                "blueprint": {
                    "candidates": [candidate],
                },
            }
        )

        self.assertIsNone(
            self.planner.evaluate(context)
        )

    def test_returns_none_when_candidates_are_empty(
        self,
    ) -> None:
        context = DecisionContext(
            world_state={
                "production": {
                    "free_slots": 2,
                },
                "blueprint": {
                    "candidates": [],
                },
            }
        )

        self.assertIsNone(
            self.planner.evaluate(context)
        )

    def test_returns_none_when_stage_is_complete(
        self,
    ) -> None:
        candidate = make_candidate(
            name="Bleakspire Roots",
            tier=11,
            craft_time_seconds=39600,
            current_progress=6,
            current_target=6,
        )

        context = DecisionContext(
            world_state={
                "production": {
                    "free_slots": 2,
                },
                "blueprint": {
                    "candidates": [candidate],
                },
            }
        )

        self.assertIsNone(
            self.planner.evaluate(context)
        )

    def test_creates_blueprint_craft_decision(
        self,
    ) -> None:
        candidate = make_candidate(
            name="Bleakspire Roots",
            tier=11,
            craft_time_seconds=39600,
            current_progress=4,
            current_target=6,
            row=1,
            column=2,
        )

        context = DecisionContext(
            world_state={
                "production": {
                    "free_slots": 2,
                },
                "blueprint": {
                    "candidates": [candidate],
                },
            }
        )

        decision = self.planner.evaluate(context)

        self.assertIsNotNone(decision)
        assert decision is not None

        self.assertEqual(
            "blueprint",
            decision.planner,
        )

        self.assertEqual(
            "CRAFT",
            decision.action,
        )

        self.assertEqual(
            "Bleakspire Roots",
            decision.payload["target_item"],
        )

        self.assertEqual(
            1,
            decision.payload["requested_count"],
        )

        self.assertEqual(
            2,
            decision.payload[
                "remaining_stage_crafts"
            ],
        )

        self.assertEqual(
            "blueprint_milestone",
            decision.payload["source"],
        )

        self.assertEqual(
            1,
            decision.payload["blueprint_row"],
        )

        self.assertEqual(
            2,
            decision.payload["blueprint_column"],
        )

    def test_selects_shortest_stage_time(
        self,
    ) -> None:
        slow = make_candidate(
            name="Opulent Decoction",
            tier=12,
            craft_time_seconds=66600,
            current_progress=4,
            current_target=6,
        )

        fast = make_candidate(
            name="Bleakspire Roots",
            tier=11,
            craft_time_seconds=39600,
            current_progress=4,
            current_target=6,
        )

        context = DecisionContext(
            world_state={
                "production": {
                    "free_slots": 2,
                },
                "blueprint": {
                    "candidates": [
                        slow,
                        fast,
                    ],
                },
            }
        )

        decision = self.planner.evaluate(context)

        self.assertIsNotNone(decision)
        assert decision is not None

        self.assertEqual(
            "Bleakspire Roots",
            decision.payload["target_item"],
        )

    def test_requested_count_is_one_even_with_many_slots(
        self,
    ) -> None:
        candidate = make_candidate(
            name="Bleakspire Roots",
            tier=11,
            craft_time_seconds=39600,
            current_progress=1,
            current_target=6,
        )

        context = DecisionContext(
            world_state={
                "production": {
                    "free_slots": 10,
                },
                "blueprint": {
                    "candidates": [candidate],
                },
            }
        )

        decision = self.planner.evaluate(context)

        self.assertIsNotNone(decision)
        assert decision is not None

        self.assertEqual(
            1,
            decision.payload["requested_count"],
        )

        self.assertEqual(
            5,
            decision.payload[
                "remaining_stage_crafts"
            ],
        )

    def test_reads_blueprint_from_metadata(
        self,
    ) -> None:
        candidate = make_candidate(
            name="Bleakspire Roots",
            tier=11,
            craft_time_seconds=39600,
            current_progress=4,
            current_target=6,
        )

        context = DecisionContext(
            world_state={},
            metadata={
                "production": {
                    "free_slots": 2,
                },
                "blueprint": {
                    "candidates": [candidate],
                },
            },
        )

        decision = self.planner.evaluate(context)

        self.assertIsNotNone(decision)

    def test_blueprint_free_slots_can_be_local(
        self,
    ) -> None:
        candidate = make_candidate(
            name="Bleakspire Roots",
            tier=11,
            craft_time_seconds=39600,
            current_progress=4,
            current_target=6,
        )

        context = DecisionContext(
            world_state={
                "blueprint": {
                    "free_slots": 1,
                    "candidates": [candidate],
                }
            }
        )

        decision = self.planner.evaluate(context)

        self.assertIsNotNone(decision)

    def test_ignores_unknown_candidate_objects(
        self,
    ) -> None:
        context = DecisionContext(
            world_state={
                "production": {
                    "free_slots": 2,
                },
                "blueprint": {
                    "candidates": [
                        {"item": "Fake Item"},
                        "invalid",
                        123,
                    ],
                },
            }
        )

        self.assertIsNone(
            self.planner.evaluate(context)
        )


if __name__ == "__main__":
    unittest.main()