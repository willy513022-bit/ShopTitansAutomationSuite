from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from planner.blueprint_models import BlueprintProgress
from planner.blueprint_planner import BlueprintPlanner
from vision.blueprint_progress_detector import (
    BlueprintProgressDetector,
)
from vision.blueprint_progress_models import (
    ImageRegion,
)
from vision.blueprint_progress_regions import (
    BlueprintProgressRegionLocator,
)
from vision.capture import screenshot


WINDOW_TITLE = "Shop Titans"

CONFIG_PATH = (
    PROJECT_ROOT
    / "config"
    / "blueprint_card_region.json"
)

DEBUG_DIR = (
    PROJECT_ROOT
    / "screenshots"
)

DEBUG_FULL_PATH = (
    DEBUG_DIR
    / "blueprint_progress_debug.png"
)

DEBUG_CARD_PATH = (
    DEBUG_DIR
    / "blueprint_progress_card.png"
)

DEBUG_PROGRESS_PATH = (
    DEBUG_DIR
    / "blueprint_progress_crop.png"
)


def load_card_region() -> ImageRegion:
    """
    從先前框選工具產生的 JSON 載入卡片區域。
    """

    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            "找不到 blueprint_card_region.json。\n"
            "請先執行：\n"
            "python examples\\select_blueprint_card_region.py"
        )

    payload = json.loads(
        CONFIG_PATH.read_text(
            encoding="utf-8"
        )
    )

    region = payload["card_region"]

    return ImageRegion(
        x=int(region["x"]),
        y=int(region["y"]),
        width=int(region["width"]),
        height=int(region["height"]),
    )


def crop_region(
    image,
    region: ImageRegion,
):
    """
    從完整畫面裁切指定區域。
    """

    image_height, image_width = (
        image.shape[:2]
    )

    left = max(
        0,
        region.left,
    )

    top = max(
        0,
        region.top,
    )

    right = min(
        image_width,
        region.right,
    )

    bottom = min(
        image_height,
        region.bottom,
    )

    if right <= left or bottom <= top:
        return image[0:0, 0:0].copy()

    return image[
        top:bottom,
        left:right,
    ].copy()


def draw_debug(
    frame,
    *,
    card_region: ImageRegion,
    progress_region: ImageRegion,
):
    """
    建立除錯圖：

    紅框 = 整張製作卡片
    綠框 = 預估 Blueprint Progress OCR 區域
    """

    debug = frame.copy()

    # Card rectangle
    cv2.rectangle(
        debug,
        (
            card_region.left,
            card_region.top,
        ),
        (
            card_region.right,
            card_region.bottom,
        ),
        (0, 0, 255),
        3,
    )

    cv2.putText(
        debug,
        "CARD",
        (
            card_region.left,
            max(
                30,
                card_region.top - 10,
            ),
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 255),
        2,
        cv2.LINE_AA,
    )

    # Progress rectangle
    cv2.rectangle(
        debug,
        (
            progress_region.left,
            progress_region.top,
        ),
        (
            progress_region.right,
            progress_region.bottom,
        ),
        (0, 255, 0),
        3,
    )

    cv2.putText(
        debug,
        "PROGRESS",
        (
            progress_region.left,
            max(
                30,
                progress_region.top - 10,
            ),
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )

    return debug


def main() -> int:
    print("=" * 72)
    print(" Blueprint Progress Vision Demo")
    print("=" * 72)

    #
    # Load selected card region
    #

    try:
        card_region = load_card_region()

    except Exception as error:
        print()
        print("[ERROR] 無法讀取卡片區域。")
        print(error)
        return 1

    print()
    print("Card region")
    print("-" * 72)

    print(
        f"x      : {card_region.x}"
    )
    print(
        f"y      : {card_region.y}"
    )
    print(
        f"width  : {card_region.width}"
    )
    print(
        f"height : {card_region.height}"
    )

    #
    # Capture
    #

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

    frame_height, frame_width = (
        frame.shape[:2]
    )

    print(
        f"Capture size: "
        f"{frame_width} x {frame_height}"
    )

    DEBUG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    #
    # Validate selected card
    #

    if (
        card_region.right > frame_width
        or card_region.bottom > frame_height
    ):
        print()
        print(
            "[ERROR] 儲存的卡片區域超出目前擷取畫面。"
        )

        print(
            "可能是遊戲視窗大小或位置改變。"
        )

        print(
            "請重新執行："
        )

        print(
            "python examples\\select_blueprint_card_region.py"
        )

        return 1

    #
    # Save card crop
    #

    card_image = crop_region(
        frame,
        card_region,
    )

    cv2.imwrite(
        str(DEBUG_CARD_PATH),
        card_image,
    )

    #
    # Locate expected progress region
    #

    locator = (
        BlueprintProgressRegionLocator()
    )

    progress_region = locator.locate(
        card_region
    )

    print()
    print("Progress region")
    print("-" * 72)

    print(
        f"x      : {progress_region.x}"
    )
    print(
        f"y      : {progress_region.y}"
    )
    print(
        f"width  : {progress_region.width}"
    )
    print(
        f"height : {progress_region.height}"
    )

    #
    # Save raw progress crop
    #

    progress_image = crop_region(
        frame,
        progress_region,
    )

    cv2.imwrite(
        str(DEBUG_PROGRESS_PATH),
        progress_image,
    )

    #
    # Save full debug image
    #

    debug = draw_debug(
        frame,
        card_region=card_region,
        progress_region=progress_region,
    )

    cv2.imwrite(
        str(DEBUG_FULL_PATH),
        debug,
    )

    #
    # Vision detector
    #

    print()
    print("Running RapidOCR...")
    print("-" * 72)

    detector = (
        BlueprintProgressDetector()
    )

    detection = detector.detect(
        image=frame,
        card_region=card_region,
    )

    print()
    print("OCR result")
    print("=" * 72)

    print(
        f"OCR text       : "
        f"{detection.ocr_text!r}"
    )

    print(
        f"OCR confidence : "
        f"{detection.ocr_confidence:.4f}"
    )

    print(
        f"Parsed         : "
        f"{detection.detected}"
    )

    #
    # Parse result
    #

    if detection.parsed is None:
        print()
        print(
            "[WARNING] 沒有成功解析 Blueprint Progress。"
        )

        print()
        print(
            "請先查看這張圖片："
        )

        print(
            DEBUG_PROGRESS_PATH
        )

        print()
        print(
            "確認圖片內是否有完整的 N/N，"
            "例如 2/4。"
        )

        print()
        print("Debug files")
        print("-" * 72)

        print(
            f"Full     : {DEBUG_FULL_PATH}"
        )
        print(
            f"Card     : {DEBUG_CARD_PATH}"
        )
        print(
            f"Progress : {DEBUG_PROGRESS_PATH}"
        )

        return 0

    parsed = detection.parsed

    print()
    print("Parsed progress")
    print("=" * 72)

    print(
        f"Current   : "
        f"{parsed.current_progress}"
    )

    print(
        f"Target    : "
        f"{parsed.current_target}"
    )

    print(
        f"Remaining : "
        f"{parsed.remaining}"
    )

    print(
        f"Complete  : "
        f"{parsed.complete}"
    )

    #
    # Feed into BlueprintPlanner
    #

    progress = BlueprintProgress(
        item_name="Selected Blueprint",
        current_progress=(
            parsed.current_progress
        ),
        current_target=(
            parsed.current_target
        ),
        source=(
            "blueprint_progress_vision_demo"
        ),
        confidence=(
            detection.ocr_confidence
        ),
    )

    planner = BlueprintPlanner()

    plan = planner.build_plan(
        progress
    )

    print()
    print("Blueprint Planner")
    print("=" * 72)

    print(
        f"Action           : "
        f"{plan.action.value}"
    )

    print(
        f"Crafts remaining : "
        f"{plan.crafts_remaining}"
    )

    print(
        f"Collection ready : "
        f"{plan.collection_unlocked}"
    )

    print(
        f"Rescan afterward : "
        f"{plan.should_rescan_after_execution}"
    )

    print()
    print(
        f"Reason : {plan.reason}"
    )

    #
    # Expected check for current sample
    #

    print()
    print("Expected for current sample")
    print("=" * 72)

    print(
        "Jindai Zakura 畫面目前應為：2/4"
    )

    if (
        parsed.current_progress == 2
        and parsed.current_target == 4
    ):
        print()
        print(
            "[SUCCESS] 真實遊戲畫面成功辨識 2/4！"
        )

    else:
        print()
        print(
            "[INFO] OCR 有辨識到進度，"
            "但目前結果不是預期的 2/4。"
        )

    print()
    print("Debug files")
    print("=" * 72)

    print(
        f"Full     : {DEBUG_FULL_PATH}"
    )

    print(
        f"Card     : {DEBUG_CARD_PATH}"
    )

    print(
        f"Progress : {DEBUG_PROGRESS_PATH}"
    )

    print()
    print("=" * 72)
    print("Demo finished.")
    print("=" * 72)

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )