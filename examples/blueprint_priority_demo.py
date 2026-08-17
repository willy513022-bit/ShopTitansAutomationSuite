from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from planner.blueprint_candidate import (
    BlueprintCandidate,
)
from planner.blueprint_priority import (
    BlueprintPriorityScorer,
)
from services.blueprint_name_matcher import (
    BlueprintNameMatcher,
)
from services.game_data_service import (
    game_data_service,
)
from vision.blueprint_card_locator import (
    BlueprintCardLocator,
)
from vision.blueprint_card_scanner import (
    BlueprintCardScanner,
)
from vision.blueprint_name_detector import (
    BlueprintNameDetector,
)
from vision.capture import screenshot


WINDOW_TITLE = "Shop Titans"

FIRST_CARD_X = 16
FIRST_CARD_Y = 1011
MAXIMUM_ROWS = 10


def format_seconds(
    seconds: int,
) -> str:
    if seconds < 60:
        return f"{seconds}s"

    minutes, second = divmod(
        seconds,
        60,
    )

    if minutes < 60:
        return (
            f"{minutes}m "
            f"{second}s"
        )

    hours, minute = divmod(
        minutes,
        60,
    )

    if hours < 24:
        return (
            f"{hours}h "
            f"{minute}m"
        )

    days, hour = divmod(
        hours,
        24,
    )

    return (
        f"{days}d "
        f"{hour}h "
        f"{minute}m"
    )


def main() -> int:
    print("=" * 90)
    print(" Blueprint Priority Demo")
    print("=" * 90)

    frame = screenshot(
        WINDOW_TITLE
    )

    if frame is None:
        print(
            "[ERROR] Could not capture Shop Titans."
        )
        return 1

    height, width = (
        frame.shape[:2]
    )

    cards = (
        BlueprintCardLocator()
        .locate(
            first_card_x=FIRST_CARD_X,
            first_card_y=FIRST_CARD_Y,
            image_width=width,
            image_height=height,
            maximum_rows=MAXIMUM_ROWS,
        )
    )

    all_names = tuple(
        item.name
        for item
        in game_data_service.get_all()
    )

    scanner = BlueprintCardScanner(
        name_detector=(
            BlueprintNameDetector(
                matcher=(
                    BlueprintNameMatcher(
                        all_names,
                        minimum_score=0.70,
                    )
                )
            )
        )
    )

    states = scanner.scan(
        image=frame,
        cards=cards,
    )

    candidates = []

    for state in states:
        if not state.valid:
            continue

        assert state.item_name is not None

        item = (
            game_data_service
            .get_by_name(
                state.item_name
            )
        )

        if item is None:
            print(
                "[WARNING] Missing GameItem:",
                state.item_name,
            )
            continue

        candidate = BlueprintCandidate(
            state=state,
            item=item,
        )

        candidates.append(
            candidate
        )

    scorer = BlueprintPriorityScorer()

    ranked = scorer.rank(
        candidates
    )

    print()
    print(
        f"{'Rank':<6}"
        f"{'Name':<30}"
        f"{'Tier':<7}"
        f"{'Remain':<9}"
        f"{'Craft/item':<16}"
        f"{'Stage ETA':<16}"
    )

    print("-" * 90)

    for result in ranked:
        candidate = (
            result.candidate
        )

        print(
            f"{result.rank:<6}"
            f"{candidate.item_name:<30}"
            f"{candidate.tier:<7}"
            f"{candidate.remaining:<9}"
            f"{format_seconds(candidate.craft_time_seconds):<16}"
            f"{format_seconds(candidate.estimated_stage_time_seconds):<16}"
        )

    print()
    print("=" * 90)
    print(" Selected Blueprint Target")
    print("=" * 90)

    best = scorer.select_best(
        candidates
    )

    if best is None:
        print(
            "No valid Blueprint candidate."
        )
        return 0

    print(
        f"Name       : {best.item_name}"
    )

    print(
        f"Tier       : {best.tier}"
    )

    print(
        f"Progress   : "
        f"{best.state.progress_text}"
    )

    print(
        f"Remaining  : "
        f"{best.remaining}"
    )

    print(
        f"Craft/item : "
        f"{format_seconds(best.craft_time_seconds)}"
    )

    print(
        f"Stage ETA  : "
        f"{format_seconds(best.estimated_stage_time_seconds)}"
    )

    print()
    print(
        "Reason     : shortest estimated current-stage "
        "craft time, then lower tier, then fewer "
        "remaining crafts."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )