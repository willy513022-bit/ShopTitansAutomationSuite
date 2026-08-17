from __future__ import annotations

import sys
from pathlib import Path

import cv2


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from services.blueprint_name_matcher import (
    BlueprintNameMatcher,
)
from vision.blueprint_card_locator import (
    BlueprintCardLocator,
)
from vision.blueprint_name_detector import (
    BlueprintNameDetector,
)
from vision.blueprint_progress_detector import (
    BlueprintProgressDetector,
)
from vision.capture import screenshot


WINDOW_TITLE = "Shop Titans"

DEBUG_DIR = PROJECT_ROOT / "screenshots"

DEBUG_PATH = (
    DEBUG_DIR
    / "blueprint_name_vision_debug.png"
)

FIRST_CARD_X = 16
FIRST_CARD_Y = 1011

MAXIMUM_ROWS = 10


# ============================================================
# Temporary live-test database
# ============================================================
#
# 這一版先使用目前畫面上已知的六個物品，
# 用來驗證：
#
#   1. Name Region 是否正確
#   2. RapidOCR 是否能讀到名稱
#   3. Matcher 是否能修正小型 OCR 錯誤
#   4. Name + Progress 是否能正確綁定同一張卡
#
# 真機驗證完成後，
# 下一階段會改成由正式 Blueprint database
# 自動提供所有物品名稱。
#

KNOWN_ITEM_NAMES = [
    "Angler's Veil",
    "Lost Star Chart",
    "Opulent Incantation",
    "Opulent Decoction",
    "Ice Queen's Summer Hat",
    "Bleakspire Roots",
]


def draw_region(
    image,
    *,
    region,
    color,
    thickness=2,
):
    cv2.rectangle(
        image,
        (
            region.left,
            region.top,
        ),
        (
            region.right,
            region.bottom,
        ),
        color,
        thickness,
    )


def draw_label(
    image,
    *,
    x,
    y,
    text,
    color,
):
    cv2.putText(
        image,
        text,
        (
            x,
            max(20, y),
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        color,
        1,
        cv2.LINE_AA,
    )


def main() -> int:
    print("=" * 72)
    print(" Blueprint Name + Progress Vision Demo")
    print("=" * 72)

    print()
    print("Capturing Shop Titans...")

    frame = screenshot(
        WINDOW_TITLE
    )

    if frame is None:
        print()
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

    print()
    print("Grid calibration")
    print("-" * 72)

    print(
        f"First card X : {FIRST_CARD_X}"
    )

    print(
        f"First card Y : {FIRST_CARD_Y}"
    )

    # --------------------------------------------------------
    # Locate cards
    # --------------------------------------------------------

    card_locator = BlueprintCardLocator()

    cards = card_locator.locate(
        first_card_x=FIRST_CARD_X,
        first_card_y=FIRST_CARD_Y,
        image_width=image_width,
        image_height=image_height,
        maximum_rows=MAXIMUM_ROWS,
    )

    print()
    print(
        f"Visible card regions : {len(cards)}"
    )

    if not cards:
        print()
        print(
            "[ERROR] No Blueprint card regions found."
        )
        return 1

    # --------------------------------------------------------
    # Build detectors
    # --------------------------------------------------------

    print()
    print("Loading OCR detectors...")

    matcher = BlueprintNameMatcher(
        KNOWN_ITEM_NAMES,
        minimum_score=0.70,
    )

    name_detector = BlueprintNameDetector(
        matcher=matcher,
        minimum_ocr_confidence=0.0,
        upscale=4.0,
    )

    progress_detector = (
        BlueprintProgressDetector()
    )

    print("Detectors ready.")

    debug = frame.copy()

    results = []

    name_detected_count = 0
    progress_detected_count = 0
    complete_pair_count = 0

    # --------------------------------------------------------
    # Scan every visible card
    # --------------------------------------------------------

    for index, card in enumerate(
        cards,
        start=1,
    ):
        region = card.region

        print()
        print("=" * 72)
        print(
            f" Card {index}"
        )
        print("=" * 72)

        print(
            f"Grid          : "
            f"row={card.row}, "
            f"column={card.column}"
        )

        print(
            f"Card region   : "
            f"x={region.x}, "
            f"y={region.y}, "
            f"w={region.width}, "
            f"h={region.height}"
        )

        # ----------------------------------------------------
        # Name OCR
        # ----------------------------------------------------

        name_detection = None
        name_error = None

        try:
            name_detection = (
                name_detector.detect(
                    image=frame,
                    card_region=region,
                )
            )

        except Exception as error:
            name_error = str(error)

        if name_error is not None:
            print()
            print(
                "Name OCR      : ERROR"
            )
            print(
                f"Name reason   : {name_error}"
            )

        elif name_detection is not None:
            print()
            print(
                f"Name region   : "
                f"x={name_detection.name_region.x}, "
                f"y={name_detection.name_region.y}, "
                f"w={name_detection.name_region.width}, "
                f"h={name_detection.name_region.height}"
            )

            print(
                f"Name raw      : "
                f"{name_detection.ocr_text!r}"
            )

            print(
                f"Name OCR conf : "
                f"{name_detection.ocr_confidence:.4f}"
            )

            print(
                f"Name matched  : "
                f"{name_detection.item_name!r}"
            )

            if (
                name_detection.match_score
                is not None
            ):
                print(
                    f"Match score   : "
                    f"{name_detection.match_score:.4f}"
                )
            else:
                print(
                    "Match score   : None"
                )

            if name_detection.detected:
                name_detected_count += 1

        # ----------------------------------------------------
        # Progress OCR
        # ----------------------------------------------------

        progress_detection = None
        progress_error = None

        try:
            progress_detection = (
                progress_detector.detect(
                    image=frame,
                    card_region=region,
                )
            )

        except Exception as error:
            progress_error = str(error)

        if progress_error is not None:
            print()
            print(
                "Progress OCR   : ERROR"
            )
            print(
                f"Progress reason: "
                f"{progress_error}"
            )

        elif progress_detection is not None:
            print()
            print(
                f"Progress raw  : "
                f"{progress_detection.ocr_text!r}"
            )

            print(
                f"Progress conf : "
                f"{progress_detection.ocr_confidence:.4f}"
            )

            if (
                progress_detection.parsed
                is not None
            ):
                progress = (
                    progress_detection.parsed
                )

                progress_detected_count += 1

                print(
                    f"Progress      : "
                    f"{progress.current_progress}"
                    f"/"
                    f"{progress.current_target}"
                )

                print(
                    f"Remaining     : "
                    f"{progress.remaining}"
                )

            else:
                print(
                    "Progress      : not parsed"
                )

        # ----------------------------------------------------
        # Pair result
        # ----------------------------------------------------

        pair_complete = (
            name_detection is not None
            and name_detection.detected
            and progress_detection is not None
            and progress_detection.parsed
            is not None
        )

        if pair_complete:
            complete_pair_count += 1

        results.append(
            {
                "index": index,
                "card": card,
                "name": name_detection,
                "progress": progress_detection,
                "name_error": name_error,
                "progress_error": progress_error,
                "pair_complete": pair_complete,
            }
        )

        # ----------------------------------------------------
        # Debug drawing
        # ----------------------------------------------------

        if pair_complete:
            card_color = (
                0,
                255,
                0,
            )
        else:
            card_color = (
                0,
                165,
                255,
            )

        draw_region(
            debug,
            region=region,
            color=card_color,
            thickness=2,
        )

        if name_detection is not None:
            draw_region(
                debug,
                region=(
                    name_detection.name_region
                ),
                color=(
                    255,
                    255,
                    0,
                ),
                thickness=2,
            )

        if (
            progress_detection
            is not None
        ):
            draw_region(
                debug,
                region=(
                    progress_detection
                    .progress_region
                ),
                color=(
                    255,
                    0,
                    255,
                ),
                thickness=2,
            )

        if (
            name_detection is not None
            and name_detection.item_name
        ):
            short_name = (
                name_detection.item_name
            )
        else:
            short_name = "UNKNOWN"

        if (
            progress_detection
            is not None
            and progress_detection.parsed
            is not None
        ):
            progress = (
                progress_detection.parsed
            )

            progress_text = (
                f"{progress.current_progress}"
                f"/"
                f"{progress.current_target}"
            )

        else:
            progress_text = "?/?"

        draw_label(
            debug,
            x=region.left + 3,
            y=region.top + 18,
            text=(
                f"C{index} "
                f"{short_name} "
                f"{progress_text}"
            ),
            color=card_color,
        )

    # --------------------------------------------------------
    # Save debug image
    # --------------------------------------------------------

    DEBUG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    cv2.imwrite(
        str(DEBUG_PATH),
        debug,
    )

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    print()
    print()
    print("=" * 72)
    print(" Blueprint Card State Summary")
    print("=" * 72)

    for result in results:
        index = result["index"]

        name_detection = result[
            "name"
        ]

        progress_detection = result[
            "progress"
        ]

        if (
            name_detection is not None
            and name_detection.item_name
        ):
            item_name = (
                name_detection.item_name
            )
        else:
            item_name = "UNKNOWN"

        if (
            progress_detection is not None
            and progress_detection.parsed
            is not None
        ):
            progress = (
                progress_detection.parsed
            )

            progress_text = (
                f"{progress.current_progress}"
                f"/"
                f"{progress.current_target}"
            )

            remaining_text = str(
                progress.remaining
            )

        else:
            progress_text = "?/?"
            remaining_text = "?"

        print(
            f"Card {index:<2} | "
            f"{item_name:<26} | "
            f"{progress_text:<7} | "
            f"remaining={remaining_text}"
        )

    print()
    print("-" * 72)

    print(
        f"Cards located      : "
        f"{len(cards)}"
    )

    print(
        f"Names detected     : "
        f"{name_detected_count}"
    )

    print(
        f"Progress detected  : "
        f"{progress_detected_count}"
    )

    print(
        f"Complete pairs     : "
        f"{complete_pair_count}"
        f"/"
        f"{len(cards)}"
    )

    print()
    print("Debug legend")
    print("-" * 72)
    print(
        "Green card   = name + progress both detected"
    )
    print(
        "Orange card  = incomplete detection"
    )
    print(
        "Cyan box     = name OCR region"
    )
    print(
        "Magenta box  = progress OCR region"
    )

    print()
    print(
        f"Debug image:"
    )
    print(
        DEBUG_PATH
    )

    print()
    print("=" * 72)

    if (
        complete_pair_count
        == len(cards)
        and len(cards) > 0
    ):
        print(
            "[SUCCESS] Every visible Blueprint card "
            "has name + progress."
        )

    elif complete_pair_count > 0:
        print(
            "[PARTIAL] Some Blueprint cards have "
            "name + progress."
        )

    else:
        print(
            "[INFO] Card grid works, but name/progress "
            "pairing still needs calibration."
        )

    print("=" * 72)

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )