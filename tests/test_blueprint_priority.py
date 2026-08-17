import pytest

from models.game_item import GameItem
from planner.blueprint_candidate import (
    BlueprintCandidate,
)
from planner.blueprint_priority import (
    BlueprintPriorityScorer,
)
from vision.blueprint_card_scanner import (
    BlueprintCardState,
)
from vision.blueprint_progress_models import (
    ImageRegion,
)


def make_state(
    *,
    item_name: str,
    remaining: int,
    row: int = 0,
    column: int = 0,
):
    target = max(
        1,
        remaining,
    )

    current = 0

    if remaining == 0:
        target = 1
        current = 1

    return BlueprintCardState(
        row=row,
        column=column,
        card_region=ImageRegion(
            x=0,
            y=0,
            width=207,
            height=250,
        ),
        item_name=item_name,
        current_progress=current,
        current_target=target,
        remaining=remaining,
        name_confidence=1.0,
        progress_confidence=1.0,
    )


def make_item(
    *,
    name: str,
    tier: int,
    craft_time_seconds: int,
):
    return GameItem(
        item_id=(
            name.lower()
            .replace(" ", "_")
            .replace("'", "")
        ),
        name=name,
        item_type="Test",
        tier=tier,
        craft_time_seconds=craft_time_seconds,
    )


def make_candidate(
    *,
    name: str,
    tier: int,
    craft_time_seconds: int,
    remaining: int,
):
    return BlueprintCandidate(
        state=make_state(
            item_name=name,
            remaining=remaining,
        ),
        item=make_item(
            name=name,
            tier=tier,
            craft_time_seconds=(
                craft_time_seconds
            ),
        ),
    )


def test_estimated_stage_time():
    candidate = make_candidate(
        name="Example",
        tier=3,
        craft_time_seconds=15,
        remaining=4,
    )

    assert (
        candidate.estimated_stage_time_seconds
        == 60
    )


def test_shorter_total_time_wins_even_with_more_remaining():
    fast = make_candidate(
        name="Fast Low Tier",
        tier=1,
        craft_time_seconds=15,
        remaining=4,
    )

    slow = make_candidate(
        name="Slow High Tier",
        tier=12,
        craft_time_seconds=66600,
        remaining=2,
    )

    best = (
        BlueprintPriorityScorer()
        .select_best(
            [
                slow,
                fast,
            ]
        )
    )

    assert best is fast


def test_lower_tier_breaks_equal_time_tie():
    low = make_candidate(
        name="Low",
        tier=2,
        craft_time_seconds=30,
        remaining=2,
    )

    high = make_candidate(
        name="High",
        tier=8,
        craft_time_seconds=20,
        remaining=3,
    )

    # Both = 60 seconds.
    best = (
        BlueprintPriorityScorer()
        .select_best(
            [
                high,
                low,
            ]
        )
    )

    assert best is low


def test_remaining_breaks_equal_time_and_tier_tie():
    fewer = make_candidate(
        name="Fewer",
        tier=3,
        craft_time_seconds=30,
        remaining=2,
    )

    more = make_candidate(
        name="More",
        tier=3,
        craft_time_seconds=20,
        remaining=3,
    )

    # Both = 60 seconds and same tier.
    best = (
        BlueprintPriorityScorer()
        .select_best(
            [
                more,
                fewer,
            ]
        )
    )

    assert best is fewer


def test_name_breaks_full_tie():
    alpha = make_candidate(
        name="Alpha",
        tier=3,
        craft_time_seconds=30,
        remaining=2,
    )

    beta = make_candidate(
        name="Beta",
        tier=3,
        craft_time_seconds=30,
        remaining=2,
    )

    best = (
        BlueprintPriorityScorer()
        .select_best(
            [
                beta,
                alpha,
            ]
        )
    )

    assert best is alpha


def test_rank_assigns_order():
    a = make_candidate(
        name="A",
        tier=1,
        craft_time_seconds=10,
        remaining=1,
    )

    b = make_candidate(
        name="B",
        tier=1,
        craft_time_seconds=20,
        remaining=1,
    )

    ranked = (
        BlueprintPriorityScorer()
        .rank(
            [
                b,
                a,
            ]
        )
    )

    assert ranked[0].rank == 1
    assert ranked[0].candidate is a

    assert ranked[1].rank == 2
    assert ranked[1].candidate is b


def test_empty_candidates_returns_none():
    assert (
        BlueprintPriorityScorer()
        .select_best([])
        is None
    )


def test_candidate_requires_valid_state():
    invalid_state = BlueprintCardState(
        row=0,
        column=0,
        card_region=ImageRegion(
            x=0,
            y=0,
            width=207,
            height=250,
        ),
        item_name=None,
        current_progress=None,
        current_target=None,
        remaining=None,
        name_confidence=0.0,
        progress_confidence=0.0,
    )

    with pytest.raises(ValueError):
        BlueprintCandidate(
            state=invalid_state,
            item=make_item(
                name="Example",
                tier=1,
                craft_time_seconds=10,
            ),
        )


def test_candidate_requires_matching_names():
    with pytest.raises(ValueError):
        BlueprintCandidate(
            state=make_state(
                item_name="Vision Name",
                remaining=1,
            ),
            item=make_item(
                name="Database Name",
                tier=1,
                craft_time_seconds=10,
            ),
        )


def test_sort_key_rejects_unknown_object():
    with pytest.raises(TypeError):
        BlueprintPriorityScorer.sort_key(
            object()
        )