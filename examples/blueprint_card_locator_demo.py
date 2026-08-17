from __future__ import annotations

import sys
from pathlib import Path

import cv2


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from vision.capture import screenshot
from vision.blueprint_card_locator import (
    BlueprintCardLocator,
)
from vision.blueprint_progress_detector import (
    BlueprintProgressDetector,
)


WINDOW_TITLE = "Shop Titans"

DEBUG_DIR = PROJECT_ROOT / "screenshots"

DEBUG_PATH = (
    DEBUG_DIR
    / "blueprint_card_locator_debug.png"
)


# ============================================================
# Live calibration
# ============================================================
#
# 已經由真實畫面人工確認：
#
# Jindai Zakura
#
# x = 438
# y = 1273
# w = 207
# h = 250
#
# 它是：
#
#   第 3 欄
#   下方那一列
#
# BlueprintCardLocator 預設：
#
# column_step = 211
# row_step    = 262
#
# 因此反推：
#
# 第一欄：
#
# 438 - (2 * 211)
# = 16
#
# 上一列：
#
# 1273 - 262
# = 1011
#
# 所以目前可見 Grid anchor：
#
FIRST_CARD_X = 16
FIRST_CARD_Y = 1011

MAXIMUM_ROWS = 10


def draw_card(
    image,
    *,
    card,
    label: str,
    parsed: bool,
):
    region = card.region

    if parsed:
        color = (0, 255, 0)
    else:
        color = (0, 165, 255)

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
        3,
    )

    label_y = max(
        25,
        region.top + 25,
    )

    cv2.putText(
        image,
        label,
        (
            region.left + 5,
            label_y,
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        color,
        2,
        cv2.LINE_AA,
    )


def main() -> int:
    print("=" * 72)
    print(" Blueprint Card Locator - Live Demo")
    print("=" * 72)

    print()
    print("Capturing Shop Titans...")

    frame = screenshot(
        WINDOW_TITLE
    )

    if frame is None:
        print()
        print(
            "[ERROR] 無法擷取 Shop Titans。"
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

    #
    # Locate cards
    #

    locator = BlueprintCardLocator()

    cards = locator.locate(
        first_card_x=FIRST_CARD_X,
        first_card_y=FIRST_CARD_Y,
        image_width=image_width,
        image_height=image_height,
        maximum_rows=MAXIMUM_ROWS,
    )

    print()
    print("=" * 72)
    print(" Located Cards")
    print("=" * 72)

    print(
        f"Detected regions: {len(cards)}"
    )

    if not cards:
        print()
        print(
            "[ERROR] 沒有產生任何 Blueprint Card region。"
        )
        return 1

    #
    # OCR detector
    #

    print()
    print("Loading Blueprint Progress Detector...")

    detector = (
        BlueprintProgressDetector()
    )

    print("Detector ready.")

    debug = frame.copy()

    parsed_count = 0

    results = []

    #
    # Process every visible card
    #

    for index, card in enumerate(
        cards,
        start=1,
    ):
        region = card.region

        print()
        print("-" * 72)

        print(
            f"Card {index}"
        )

        print(
            f"Grid    : "
            f"row={card.row}, "
            f"column={card.column}"
        )

        print(
            f"Region  : "
            f"x={region.x}, "
            f"y={region.y}, "
            f"w={region.width}, "
            f"h={region.height}"
        )

        try:
            detection = detector.detect(
                image=frame,
                card_region=region,
            )

        except Exception as error:
            print(
                f"OCR     : ERROR"
            )

            print(
                f"Reason  : {error}"
            )

            draw_card(
                debug,
                card=card,
                label=f"C{index} ERROR",
                parsed=False,
            )

            results.append(
                {
                    "index": index,
                    "card": card,
                    "detection": None,
                    "error": str(error),
                }
            )

            continue

        print(
            f"OCR     : "
            f"{detection.ocr_text!r}"
        )

        print(
            f"Conf    : "
            f"{detection.ocr_confidence:.4f}"
        )

        if detection.parsed is None:
            print(
                "Progress: not parsed"
            )

            label = (
                f"C{index} ?/?"
            )

            draw_card(
                debug,
                card=card,
                label=label,
                parsed=False,
            )

            results.append(
                {
                    "index": index,
                    "card": card,
                    "detection": detection,
                    "error": None,
                }
            )

            continue

        progress = detection.parsed

        parsed_count += 1

        print(
            f"Progress: "
            f"{progress.current_progress}"
            f"/"
            f"{progress.current_target}"
        )

        print(
            f"Remaining: "
            f"{progress.remaining}"
        )

        print(
            f"Complete : "
            f"{progress.complete}"
        )

        label = (
            f"C{index} "
            f"{progress.current_progress}"
            f"/"
            f"{progress.current_target}"
        )

        draw_card(
            debug,
            card=card,
            label=label,
            parsed=True,
        )

        results.append(
            {
                "index": index,
                "card": card,
                "detection": detection,
                "error": None,
            }
        )

    #
    # Save debug screenshot
    #

    DEBUG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    cv2.imwrite(
        str(DEBUG_PATH),
        debug,
    )

    #
    # Summary
    #

    print()
    print("=" * 72)
    print(" Blueprint Progress Summary")
    print("=" * 72)

    for result in results:
        index = result["index"]

        detection = result[
            "detection"
        ]

        error = result[
            "error"
        ]

        if error is not None:
            print(
                f"Card {index:<2} : ERROR"
            )
            continue

        if (
            detection is None
            or detection.parsed is None
        ):
            print(
                f"Card {index:<2} : "
                f"no progress"
            )
            continue

        progress = detection.parsed

        print(
            f"Card {index:<2} : "
            f"{progress.current_progress}"
            f"/"
            f"{progress.current_target}"
            f"  remaining="
            f"{progress.remaining}"
        )

    print()
    print("-" * 72)

    print(
        f"Regions generated : "
        f"{len(cards)}"
    )

    print(
        f"Progress detected : "
        f"{parsed_count}"
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

    if parsed_count:
        print(
            "[SUCCESS] 至少一張真實 Blueprint "
            "卡片成功讀取進度。"
        )
    else:
        print(
            "[INFO] Grid 已建立，但目前沒有卡片 "
            "成功解析 N/N。"
        )

    print("=" * 72)

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )