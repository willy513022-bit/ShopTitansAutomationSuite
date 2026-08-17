from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from services.blueprint_name_matcher import (
    BlueprintNameMatcher,
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


KNOWN_ITEM_NAMES = [
    "Angler's Veil",
    "Lost Star Chart",
    "Opulent Incantation",
    "Opulent Decoction",
    "Ice Queen's Summer Hat",
    "Bleakspire Roots",
]


def main() -> int:
    print("=" * 72)
    print(" Blueprint Card Scanner Demo")
    print("=" * 72)

    print()
    print("Capturing Shop Titans...")

    frame = screenshot(
        WINDOW_TITLE
    )

    if frame is None:
        print(
            "[ERROR] Could not capture Shop Titans."
        )
        return 1

    image_height, image_width = (
        frame.shape[:2]
    )

    print(
        f"Capture size : "
        f"{image_width} x {image_height}"
    )

    locator = BlueprintCardLocator()

    cards = locator.locate(
        first_card_x=FIRST_CARD_X,
        first_card_y=FIRST_CARD_Y,
        image_width=image_width,
        image_height=image_height,
        maximum_rows=MAXIMUM_ROWS,
    )

    print(
        f"Cards located: {len(cards)}"
    )

    matcher = BlueprintNameMatcher(
        KNOWN_ITEM_NAMES,
        minimum_score=0.70,
    )

    scanner = BlueprintCardScanner(
        name_detector=(
            BlueprintNameDetector(
                matcher=matcher,
            )
        )
    )

    print()
    print("Scanning cards...")

    states = scanner.scan(
        image=frame,
        cards=cards,
    )

    print()
    print("=" * 72)
    print(" Blueprint Card States")
    print("=" * 72)

    valid_count = 0

    for index, state in enumerate(
        states,
        start=1,
    ):
        if state.valid:
            valid_count += 1

        name = (
            state.item_name
            or "UNKNOWN"
        )

        remaining = (
            str(state.remaining)
            if state.remaining
            is not None
            else "?"
        )

        print(
            f"Card {index:<2} | "
            f"{name:<26} | "
            f"{state.progress_text:<7} | "
            f"remaining={remaining:<3} | "
            f"valid={state.valid}"
        )

    print()
    print("-" * 72)

    print(
        f"Cards scanned : {len(states)}"
    )

    print(
        f"Valid states  : "
        f"{valid_count}/{len(states)}"
    )

    print()
    print("=" * 72)

    if (
        states
        and valid_count
        == len(states)
    ):
        print(
            "[SUCCESS] All visible Blueprint cards "
            "were converted to BlueprintCardState."
        )
    else:
        print(
            "[PARTIAL] Some Blueprint cards "
            "still need vision calibration."
        )

    print("=" * 72)

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )