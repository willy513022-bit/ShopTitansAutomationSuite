from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 讓直接執行 examples/popup_vision_demo.py 時也能匯入專案模組
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from vision.capture import screenshot
from vision.popup_detector import PopupDetector
from vision.popup_models import PopupDetection, PopupType
from vision.template_matcher import TemplateMatcher


ASSET_DIRECTORIES = {
    PopupType.RECONNECT: PROJECT_ROOT / "assets" / "popups" / "reconnect",
    PopupType.PAID_OFFER: PROJECT_ROOT / "assets" / "popups" / "paid_offer",
    PopupType.UPGRADE_FINISHED: (
        PROJECT_ROOT / "assets" / "popups" / "upgrade_finished"
    ),
}


def register_popup_templates(detector: PopupDetector) -> int:
    """載入 assets/popups 下現有的 PNG 模板。"""

    registered_count = 0

    for popup_type, directory in ASSET_DIRECTORIES.items():
        if not directory.exists():
            print(f"[WARNING] Template directory not found: {directory}")
            continue

        for path in sorted(directory.glob("*.png")):
            detector.register_file(
                popup_type=popup_type,
                path=path,
                template_id=path.stem,
            )
            registered_count += 1
            print(
                f"[LOADED] {popup_type.value:<18} "
                f"{path.name}"
            )

    return registered_count


def print_detection(detection: PopupDetection) -> None:
    print()
    print("=== Popup Detection ===")
    print(f"Type       : {detection.popup_type.value}")
    print(f"Template   : {detection.template_id}")
    print(f"Confidence : {detection.confidence:.4f}")
    print(f"Location   : {detection.location}")
    print(f"Size       : {detection.size}")

    if detection.location is not None and detection.size is not None:
        left, top = detection.location
        width, height = detection.size

        center = (
            left + width // 2,
            top + height // 2,
        )
        print(f"Center     : {center}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect known popups in the Shop Titans window."
    )
    parser.add_argument(
        "--window-title",
        default="Shop Titans",
        help="Target window title. Default: Shop Titans",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.80,
        help="Template matching threshold. Default: 0.80",
    )
    args = parser.parse_args()

    if not 0.0 <= args.threshold <= 1.0:
        print("[ERROR] --threshold must be between 0.0 and 1.0")
        return 2

    detector = PopupDetector(
        matcher=TemplateMatcher(threshold=args.threshold)
    )

    template_count = register_popup_templates(detector)

    if template_count == 0:
        print("[ERROR] No popup templates were loaded.")
        return 1

    print()
    print(f"Loaded {template_count} popup templates.")
    print(f"Capturing window: {args.window_title!r}")

    frame = screenshot(args.window_title)

    if frame is None:
        print()
        print("[ERROR] Unable to capture the Shop Titans window.")
        print("確認事項：")
        print("1. Shop Titans 已經開啟。")
        print("2. 遊戲不是最小化狀態。")
        print("3. 視窗標題包含 Shop Titans。")
        return 1

    print(f"Screenshot size: {frame.shape[1]} x {frame.shape[0]}")

    detection = detector.detect_best(frame)

    if detection is None:
        print()
        print("No popup detected.")
        print(
            "可以嘗試降低門檻，例如："
            " python examples\\popup_vision_demo.py --threshold 0.70"
        )
        return 0

    print_detection(detection)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())