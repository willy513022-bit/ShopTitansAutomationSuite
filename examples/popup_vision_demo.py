from __future__ import annotations

import argparse
import ctypes
import sys
import time
from pathlib import Path
from typing import Optional

# 必須在匯入視窗／滑鼠相關套件前設定 DPI awareness。
# 讓 mss、pygetwindow 和 Windows 游標使用相同的實體像素座標。
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except (AttributeError, OSError):
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except (AttributeError, OSError):
        pass

import cv2
import pygetwindow as gw

# 讓直接執行 examples/popup_vision_demo.py 時，
# 仍可匯入專案根目錄中的模組。
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from vision.capture import screenshot
from vision.popup_detector import PopupDetector
from vision.popup_models import PopupDetection, PopupType
from vision.template_matcher import TemplateMatcher


WINDOW_TITLE = "Shop Titans"

SCREENSHOTS_DIRECTORY = PROJECT_ROOT / "screenshots"

RAW_CAPTURE_PATH = (
    SCREENSHOTS_DIRECTORY
    / "popup_debug_capture.png"
)

DEBUG_DETECTION_PATH = (
    SCREENSHOTS_DIRECTORY
    / "debug_click_position.png"
)

ASSET_DIRECTORIES = {
    PopupType.RECONNECT: (
        PROJECT_ROOT
        / "assets"
        / "popups"
        / "reconnect"
    ),
    PopupType.PAID_OFFER: (
        PROJECT_ROOT
        / "assets"
        / "popups"
        / "paid_offer"
    ),
    PopupType.UPGRADE_FINISHED: (
        PROJECT_ROOT
        / "assets"
        / "popups"
        / "upgrade_finished"
    ),
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Detect known popups in the Shop Titans window "
            "and optionally move or click the detected target."
        )
    )

    parser.add_argument(
        "--window-title",
        default=WINDOW_TITLE,
        help=f"Target window title. Default: {WINDOW_TITLE}",
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=0.80,
        help="Template matching threshold. Default: 0.80",
    )

    action_group = parser.add_mutually_exclusive_group()

    action_group.add_argument(
        "--move",
        action="store_true",
        help="Move the mouse to the detected target without clicking.",
    )

    action_group.add_argument(
        "--click",
        action="store_true",
        help="Move to and click the detected target.",
    )

    return parser.parse_args()


def register_popup_templates(
    detector: PopupDetector,
) -> int:
    """Load all PNG popup templates from assets/popups."""

    registered_count = 0

    for popup_type, directory in ASSET_DIRECTORIES.items():
        if not directory.exists():
            print(
                "[WARNING] Template directory not found: "
                f"{directory}"
            )
            continue

        template_paths = sorted(directory.glob("*.png"))

        if not template_paths:
            print(
                "[WARNING] No PNG templates found: "
                f"{directory}"
            )
            continue

        for path in template_paths:
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


def find_target_window(
    window_title: str,
):
    windows = gw.getWindowsWithTitle(window_title)

    if not windows:
        return None

    # 優先選擇可見且具有有效大小的視窗。
    for window in windows:
        if (
            window.width > 0
            and window.height > 0
            and not window.isMinimized
        ):
            return window

    return None


def calculate_detection_center(
    detection: PopupDetection,
) -> Optional[tuple[int, int]]:
    if detection.location is None or detection.size is None:
        return None

    left, top = detection.location
    width, height = detection.size

    center_x = round(left + width / 2)
    center_y = round(top + height / 2)

    return center_x, center_y


def print_detection(
    detection: PopupDetection,
    image_center: Optional[tuple[int, int]],
) -> None:
    print()
    print("=== Popup Detection ===")
    print(f"Type       : {detection.popup_type.value}")
    print(f"Template   : {detection.template_id}")
    print(f"Confidence : {detection.confidence:.4f}")
    print(f"Location   : {detection.location}")
    print(f"Size       : {detection.size}")
    print(f"Center     : {image_center}")


def save_debug_images(
    frame,
    image_center: tuple[int, int],
) -> None:
    SCREENSHOTS_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not cv2.imwrite(str(RAW_CAPTURE_PATH), frame):
        raise RuntimeError(
            f"Unable to save screenshot: {RAW_CAPTURE_PATH}"
        )

    debug_frame = frame.copy()

    cv2.circle(
        debug_frame,
        image_center,
        radius=20,
        color=(0, 0, 255),
        thickness=5,
    )

    cv2.drawMarker(
        debug_frame,
        image_center,
        color=(0, 0, 255),
        markerType=cv2.MARKER_CROSS,
        markerSize=40,
        thickness=3,
    )

    if not cv2.imwrite(
        str(DEBUG_DETECTION_PATH),
        debug_frame,
    ):
        raise RuntimeError(
            "Unable to save debug image: "
            f"{DEBUG_DETECTION_PATH}"
        )

    print()
    print(f"Raw screenshot : {RAW_CAPTURE_PATH}")
    print(f"Debug image    : {DEBUG_DETECTION_PATH}")


def image_to_screen_position(
    *,
    image_center: tuple[int, int],
    frame_width: int,
    frame_height: int,
    window,
) -> tuple[int, int]:
    """Convert captured-image coordinates to screen coordinates."""

    if window.width <= 0 or window.height <= 0:
        raise ValueError("Target window has an invalid size")

    # 通常在 DPI awareness 正確設定後會接近 1.0。
    # 仍保留比例換算，避免擷取大小與視窗回報大小略有不同。
    scale_x = frame_width / window.width
    scale_y = frame_height / window.height

    image_x, image_y = image_center

    window_relative_x = round(image_x / scale_x)
    window_relative_y = round(image_y / scale_y)

    screen_x = window.left + window_relative_x
    screen_y = window.top + window_relative_y

    print()
    print("=== Coordinate Conversion ===")
    print(
        f"Window origin   : "
        f"({window.left}, {window.top})"
    )
    print(
        f"Window size     : "
        f"({window.width}, {window.height})"
    )
    print(
        f"Capture size    : "
        f"({frame_width}, {frame_height})"
    )
    print(
        f"Scale           : "
        f"({scale_x:.4f}, {scale_y:.4f})"
    )
    print(
        f"Image center    : "
        f"({image_x}, {image_y})"
    )
    print(
        f"Window relative : "
        f"({window_relative_x}, {window_relative_y})"
    )
    print(
        f"Screen position : "
        f"({screen_x}, {screen_y})"
    )

    return screen_x, screen_y


def move_cursor(
    screen_x: int,
    screen_y: int,
) -> None:
    """Move the Windows cursor using physical screen coordinates."""

    success = ctypes.windll.user32.SetCursorPos(
        int(screen_x),
        int(screen_y),
    )

    if not success:
        raise OSError(
            "Windows SetCursorPos failed"
        )


def click_cursor() -> None:
    """Perform one left mouse click at the current cursor position."""

    mouse_event = ctypes.windll.user32.mouse_event

    mouse_event(
        0x0002,  # MOUSEEVENTF_LEFTDOWN
        0,
        0,
        0,
        0,
    )

    time.sleep(0.05)

    mouse_event(
        0x0004,  # MOUSEEVENTF_LEFTUP
        0,
        0,
        0,
        0,
    )


def main() -> int:
    args = parse_arguments()

    if not 0.0 <= args.threshold <= 1.0:
        print(
            "[ERROR] --threshold must be between "
            "0.0 and 1.0"
        )
        return 2

    detector = PopupDetector(
        matcher=TemplateMatcher(
            threshold=args.threshold,
        )
    )

    template_count = register_popup_templates(detector)

    if template_count == 0:
        print()
        print("[ERROR] No popup templates were loaded.")
        return 1

    print()
    print(f"Loaded {template_count} popup templates.")
    print(f"Capturing window: {args.window_title!r}")

    target_window = find_target_window(
        args.window_title,
    )

    if target_window is None:
        print()
        print("[ERROR] Unable to find the target window.")
        print("確認事項：")
        print("1. Shop Titans 已經開啟。")
        print("2. 遊戲不是最小化狀態。")
        print("3. 視窗標題包含 Shop Titans。")
        return 1

    frame = screenshot(args.window_title)

    if frame is None:
        print()
        print("[ERROR] Unable to capture the target window.")
        return 1

    frame_height, frame_width = frame.shape[:2]

    print(
        f"Screenshot size: "
        f"{frame_width} x {frame_height}"
    )

    detection = detector.detect_best(frame)

    if detection is None:
        SCREENSHOTS_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        cv2.imwrite(
            str(RAW_CAPTURE_PATH),
            frame,
        )

        print()
        print("No popup detected.")
        print(f"Screenshot saved: {RAW_CAPTURE_PATH}")
        print(
            "可以嘗試降低門檻，例如："
            " python examples\\popup_vision_demo.py "
            "--threshold 0.70"
        )
        return 0

    image_center = calculate_detection_center(
        detection,
    )

    print_detection(
        detection,
        image_center,
    )

    if image_center is None:
        print()
        print(
            "[ERROR] Detection has no location or size."
        )
        return 1

    save_debug_images(
        frame,
        image_center,
    )

    screen_x, screen_y = image_to_screen_position(
        image_center=image_center,
        frame_width=frame_width,
        frame_height=frame_height,
        window=target_window,
    )

    if not args.move and not args.click:
        print()
        print(
            "Detection completed. "
            "No mouse action was requested."
        )
        print(
            "Use --move to test the cursor position."
        )
        print(
            "Use --click to move and click the target."
        )
        return 0

    print()
    print(
        f"Moving cursor to "
        f"({screen_x}, {screen_y})..."
    )

    move_cursor(
        screen_x,
        screen_y,
    )

    if args.click:
        time.sleep(0.30)
        print("Clicking detected target...")
        click_cursor()
    else:
        print("Cursor moved without clicking.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())