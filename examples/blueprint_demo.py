from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from planner.blueprint_models import BlueprintProgress
from planner.blueprint_planner import BlueprintPlanner


def print_plan(
    title: str,
    progress: BlueprintProgress,
) -> None:
    planner = BlueprintPlanner()
    plan = planner.build_plan(progress)

    print()
    print("=" * 72)
    print(title)
    print("=" * 72)

    print(f"Item                 : {plan.item_name}")
    print(f"Action               : {plan.action.value}")
    print(
        f"Progress             : "
        f"{plan.current_progress}/"
        f"{plan.current_target}"
    )
    print(
        f"Completed milestones : "
        f"{plan.completed_milestones}/"
        f"{plan.total_milestones}"
    )
    print(
        f"Crafts remaining     : "
        f"{plan.crafts_remaining}"
    )
    print(
        f"Collection unlocked  : "
        f"{plan.collection_unlocked}"
    )
    print(
        f"Rescan afterwards    : "
        f"{plan.should_rescan_after_execution}"
    )
    print(f"Reason               : {plan.reason}")


def main() -> int:
    print("=" * 72)
    print(" Shop Titans Blueprint Planner Demo")
    print("=" * 72)

    print_plan(
        "Example 1 - Roland's Own",
        BlueprintProgress(
            item_name="Roland's Own",
            current_progress=10,
            current_target=15,
            completed_milestones=3,
            total_milestones=5,
            source="manual_demo",
        ),
    )

    print_plan(
        "Example 2 - New Blueprint",
        BlueprintProgress(
            item_name="Sandcastle Protector",
            current_progress=0,
            current_target=7,
            completed_milestones=0,
            total_milestones=5,
            source="manual_demo",
        ),
    )

    print_plan(
        "Example 3 - Current Stage Finished",
        BlueprintProgress(
            item_name="Example Sword",
            current_progress=15,
            current_target=15,
            completed_milestones=3,
            total_milestones=5,
            source="manual_demo",
        ),
    )

    print_plan(
        "Example 4 - All Milestones Finished",
        BlueprintProgress(
            item_name="Completed Sword",
            current_progress=None,
            current_target=None,
            completed_milestones=5,
            total_milestones=5,
            all_milestones_complete=True,
            source="manual_demo",
        ),
    )

    print()
    print("=" * 72)
    print("Demo finished.")
    print("=" * 72)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())